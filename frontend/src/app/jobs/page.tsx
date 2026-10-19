"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

interface Job {
  job_id: string;
  source: string;
  title: string;
  company: string | null;
  location: string | null;
}

interface Resume {
  resume_id: string;
  target_role: string;
  ats_score: number;
}

interface Match {
  job_id: string;
  title: string;
  company: string | null;
  match_score: number;
  match_reasons: string[];
  skill_gap: string[];
}

function scoreColor(score: number) {
  if (score >= 70) return "text-emerald-600";
  if (score >= 40) return "text-amber-600";
  return "text-rose-600";
}

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [matches, setMatches] = useState<Match[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
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
      const [jobsData, resumesData, matchesData] = await Promise.all([
        api.jobs.list(),
        api.resume.list(),
        api.matches.list().catch(() => []),
      ]);
      setJobs(jobsData);
      setResumes(resumesData);
      if (resumesData.length > 0) setResumeId(resumesData[0].resume_id);
      if (matchesData.length > 0) {
        setMatches(matchesData.map((m) => ({
          job_id: m.job_id,
          title: m.title,
          company: m.company,
          match_score: m.match_score,
          match_reasons: m.match_reasons,
          skill_gap: m.skill_gap,
        })));
      }
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }

  async function runMatching() {
    if (!resumeId) return;
    setMatching(true);
    setError("");
    try {
      const res = await api.matches.run(resumeId);
      setMatches(res.matches);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Matching failed");
    } finally {
      setMatching(false);
    }
  }

  async function apply(jobId: string) {
    if (!resumeId) return;
    setError("");
    try {
      await api.applications.create(jobId, resumeId);
      router.push("/applications");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create application");
    }
  }

  if (loading) {
    return (
      <div className="text-center py-16">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Loading jobs...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Jobs</h1>

      {resumes.length === 0 ? (
        <div className="bg-white p-8 rounded-xl shadow-sm border text-center">
          <p className="text-gray-500 mb-4">Upload a resume to match against jobs.</p>
          <Link href="/upload" className="text-indigo-600 hover:underline font-medium">
            Upload Resume →
          </Link>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-xl shadow-sm border flex flex-col md:flex-row gap-4 md:items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Match using resume</label>
            <select
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
            >
              {resumes.map((r) => (
                <option key={r.resume_id} value={r.resume_id}>
                  {r.target_role} (ATS {r.ats_score})
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={runMatching}
            disabled={matching || !resumeId}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {matching ? "Matching..." : "Run Matching"}
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {matches && (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="font-semibold">Your Matches</h2>
          </div>
          {matches.length === 0 ? (
            <p className="p-6 text-sm text-gray-500">No matches yet. Run matching above.</p>
          ) : (
            <div className="divide-y">
              {matches.map((m) => (
                <div key={m.job_id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-1">
                    <Link href={`/jobs/${m.job_id}`} className="font-medium hover:text-indigo-600">
                      {m.title}
                    </Link>
                    <span className={`font-bold ${scoreColor(m.match_score)}`}>
                      {m.match_score}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2">{m.company}</p>
                  <div className="flex flex-wrap items-center gap-2">
                    {m.skill_gap.slice(0, 4).map((s, i) => (
                      <span key={i} className="bg-rose-100 text-rose-700 text-xs px-2 py-0.5 rounded-full">
                        {s}
                      </span>
                    ))}
                    <button
                      onClick={() => apply(m.job_id)}
                      className="ml-auto text-xs text-indigo-600 hover:underline font-medium"
                    >
                      Apply →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="font-semibold">All Jobs ({jobs.length})</h2>
        </div>
        {jobs.length === 0 ? (
          <p className="p-6 text-sm text-gray-500">No jobs ingested yet.</p>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Title</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Company</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Location</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {jobs.map((j) => (
                <tr key={j.job_id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm">
                    <Link href={`/jobs/${j.job_id}`} className="text-indigo-600 hover:underline">
                      {j.title}
                    </Link>
                  </td>
                  <td className="px-6 py-3 text-sm">{j.company ?? "—"}</td>
                  <td className="px-6 py-3 text-sm text-gray-500">{j.location ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
