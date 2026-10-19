import sys
import time

sys.path.insert(0, r"C:\Users\Divyam Garg\Desktop\AI career agent\backend")

from celery.result import AsyncResult

from app.tasks.analysis_tasks import analyze_resume_task, match_jobs_task
from app.tasks.celery_app import celery_app


def await_result(task_id: str, timeout: int = 180) -> AsyncResult:
    res = AsyncResult(task_id, app=celery_app)
    start = time.time()
    while time.time() - start < timeout:
        if res.status in ("SUCCESS", "FAILURE"):
            return res
        time.sleep(2)
    raise TimeoutError(f"task {task_id} still {res.status} after {timeout}s")


m = match_jobs_task.delay("worker-u1", "worker-r1", None, 20)
print("match task:", m.id)
res = await_result(m.id)
print("match status:", res.status)
if res.status == "SUCCESS":
    print("match count:", res.result["count"])
    top = res.result["matches"][0]
    print("top:", top["title"], top["match_score"])
else:
    print("match FAILED:", str(res.result)[:300])

a = analyze_resume_task.delay("worker-u1", "worker-r1", "AI Engineer")
print("analyze task:", a.id)
res = await_result(a.id)
print("analyze status:", res.status)
if res.status == "SUCCESS":
    print("have:", res.result["have"], "| missing:", len(res.result["missing"]), "| recs:", len(res.result["recommendations"]))
else:
    print("analyze FAILED:", str(res.result)[:300])
print("WORKER E2E DONE")
