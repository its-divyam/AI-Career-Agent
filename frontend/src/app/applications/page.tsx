"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

interface Application {
  application_id: string;
  status: string;
  job_id: string;
  job_title: string;
  company: string | null;
  created_at: string | null;
}

const NEXT_STATUS: Record<string, { label: string; to: string; style: string } | null> = {
  drafted: { label: "Approve", to: "approved", style: "bg-indigo-600 hover:bg-indigo-700 text-white" },
  approved: { label: "Mark Applied", to: "applied", style: "bg-emerald-600 hover:bg-emerald-700 text-white" },
  applied: null,
  withdrawn: null,
};

function statusStyle(status: string) {
  switch (status) {
    case "approved": return "bg-indigo-100 text-indigo-800";
    case "applied": return "bg-emerald-100 text-emerald-800";
    case "withdrawn": return "bg-gray-100 text-gray-500";
    default: return "bg-amber-100 text-amber-800";
  }
}

export default function ApplicationsPage() {
  const router = useRouter();
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function load() {
    setLoading(true);
    try {
      setApps(await api.applications.list());
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }

  async function setStatus(id: string, status: string) {
    setError("");
    try {
      await api.applications.update(id, { status });
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Update failed");
    }
  }

  if (loading) {
    return (
      <div className="text-center py-16">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Loading applications...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Applications</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {apps.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm border text-center">
          <p className="text-gray-500 mb-4">No applications yet.</p>
          <Link href="/jobs" className="text-indigo-600 hover:underline font-medium">
            Browse Jobs →
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Job</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {apps.map((a) => {
                const next = NEXT_STATUS[a.status];
                return (
                  <tr key={a.application_id} className="hover:bg-gray-50">
                    <td className="px-6 py-3">
                      <Link href={`/jobs/${a.job_id}`} className="text-sm font-medium hover:text-indigo-600">
                        {a.job_title}
                      </Link>
                      <p className="text-xs text-gray-500">{a.company}</p>
                    </td>
                    <td className="px-6 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full ${statusStyle(a.status)}`}>
                        {a.status}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex gap-2">
                        {next && (
                          <button
                            onClick={() => setStatus(a.application_id, next.to)}
                            className={`text-xs px-3 py-1.5 rounded-lg font-medium ${next.style}`}
                          >
                            {next.label}
                          </button>
                        )}
                        {a.status !== "withdrawn" && a.status !== "applied" && (
                          <button
                            onClick={() => setStatus(a.application_id, "withdrawn")}
                            className="text-xs px-3 py-1.5 rounded-lg text-gray-500 hover:text-red-600 hover:bg-gray-100"
                          >
                            Withdraw
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
