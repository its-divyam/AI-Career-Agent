"use client";

import { Suspense, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useTaskPoll } from "@/lib/useTask";
import { isLoggedIn } from "@/lib/auth";

interface Recommendation {
  skill: string;
  project_idea: string;
  resource: string;
}

function SkillGapContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resumeId = searchParams.get("resume_id");
  const role = searchParams.get("role");

  const { state: task, start } = useTaskPoll();

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    if (resumeId && role) {
      start(() => api.tasks.skillGap(resumeId, role));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumeId, role]);

  const result = task.status === "success"
    ? {
        have: (task.result.have ?? []) as string[],
        missing: (task.result.missing ?? []) as string[],
        recommendations: (task.result.recommendations ?? []) as Recommendation[],
      }
    : null;
  const error = task.status === "error" ? task.error : "";
  const loading = task.status === "pending" || task.status === "idle";

  if (!resumeId || !role) {
    return (
      <div className="max-w-2xl mx-auto text-center mt-16">
        <p className="text-gray-500">No resume selected. Please upload a resume first.</p>
        <Link href="/upload" className="text-indigo-600 hover:underline mt-2 inline-block">
          Upload Resume
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Skill Gap Analysis</h1>
      <p className="text-gray-500 mb-8">
        Target role: <span className="font-medium text-gray-700">{role}</span>
      </p>

      {loading && (
        <div className="text-center py-16">
          <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Analyzing your skills against {role} requirements...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h2 className="text-lg font-semibold mb-4 text-emerald-700">
                Skills You Have ({result.have.length})
              </h2>
              <div className="flex flex-wrap gap-2">
                {result.have.length === 0 ? (
                  <p className="text-sm text-gray-500">No matching skills found</p>
                ) : (
                  result.have.map((skill, i) => (
                    <span key={i} className="bg-emerald-100 text-emerald-800 text-sm px-3 py-1 rounded-full">
                      {skill}
                    </span>
                  ))
                )}
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h2 className="text-lg font-semibold mb-4 text-rose-700">
                Skills Missing ({result.missing.length})
              </h2>
              <div className="flex flex-wrap gap-2">
                {result.missing.length === 0 ? (
                  <p className="text-sm text-gray-500">You have all required skills!</p>
                ) : (
                  result.missing.map((skill, i) => (
                    <span key={i} className="bg-rose-100 text-rose-800 text-sm px-3 py-1 rounded-full">
                      {skill}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>

          {result.recommendations.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-4">Recommendations</h2>
              <div className="space-y-4">
                {result.recommendations.map((rec, i) => (
                  <div key={i} className="bg-white p-5 rounded-xl shadow-sm border">
                    <h3 className="font-medium text-indigo-700 mb-2">{rec.skill}</h3>
                    <p className="text-sm text-gray-600 mb-2">{rec.project_idea}</p>
                    <a
                      href={rec.resource}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-indigo-500 hover:underline"
                    >
                      Find resources →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-4">
            <Link
              href="/upload"
              className="border border-gray-300 px-4 py-2 rounded-lg text-sm hover:bg-gray-100"
            >
              ← Upload New Resume
            </Link>
            <Link
              href="/dashboard"
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
            >
              Go to Dashboard →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SkillGapPage() {
  return (
    <Suspense fallback={
      <div className="max-w-4xl mx-auto text-center py-16">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Loading...</p>
      </div>
    }>
      <SkillGapContent />
    </Suspense>
  );
}
