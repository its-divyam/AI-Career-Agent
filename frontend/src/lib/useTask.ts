import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

export type TaskState =
  | { status: "idle" }
  | { status: "pending"; taskId: string }
  | { status: "success"; result: Record<string, unknown> }
  | { status: "error"; error: string };

/** Enqueue background work and poll until it resolves. Handles both
 *  PENDING (worker) and immediate SUCCESS (broker-down sync fallback). */
export function useTaskPoll(intervalMs = 2000, maxAttempts = 60) {
  const [state, setState] = useState<TaskState>({ status: "idle" });
  const attempts = useRef(0);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  function stop() {
    if (timer.current) clearInterval(timer.current);
    timer.current = null;
  }

  useEffect(() => stop, []);

  async function poll(taskId: string) {
    attempts.current += 1;
    try {
      const s = await api.tasks.status(taskId);
      if (s.status === "SUCCESS") {
        stop();
        setState({ status: "success", result: (s.result ?? {}) as Record<string, unknown> });
      } else if (s.status === "FAILURE") {
        stop();
        setState({ status: "error", error: s.error || "Task failed" });
      } else if (attempts.current >= maxAttempts) {
        stop();
        setState({ status: "error", error: "Timed out waiting for task" });
      }
    } catch (err: unknown) {
      stop();
      setState({ status: "error", error: err instanceof Error ? err.message : "Poll failed" });
    }
  }

  async function start(enqueue: () => Promise<{ task_id: string; status: string; result?: Record<string, unknown>; error?: string | null }>) {
    stop();
    attempts.current = 0;
    setState({ status: "pending", taskId: "" });
    try {
      const t = await enqueue();
      if (t.status === "SUCCESS") {
        setState({ status: "success", result: (t.result ?? {}) as Record<string, unknown> });
        return;
      }
      if (t.status === "FAILURE") {
        setState({ status: "error", error: t.error || "Task failed" });
        return;
      }
      setState({ status: "pending", taskId: t.task_id });
      timer.current = setInterval(() => poll(t.task_id), intervalMs);
    } catch (err: unknown) {
      setState({ status: "error", error: err instanceof Error ? err.message : "Enqueue failed" });
    }
  }

  function reset() {
    stop();
    setState({ status: "idle" });
  }

  return { state, start, reset };
}
