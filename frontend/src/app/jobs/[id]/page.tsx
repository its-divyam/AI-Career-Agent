"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

interface Job {
  job_id: string;
  source: string;
  title: string;
  company: string | null;
  location: string | null;
  raw_description: string | null;
  structured_requirements: { skills?: string[] } | null;
}

interface Resume {
  resume_id: string;
  target_role: string;
  ats_score: number;
}

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.id as string;

  const [job, setJob] = useState<Job | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [score, setScore] = useState<number | null>(null);
  const [gap, setGap] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  async function load() {
    setLoading(true);
    try {
      const [jobData, resumesData] = await Promise.all([
        api.jobs.get(jobId),
        api.resume.list(),
      ]);
      setJob(jobData);
      setResumes(resumesData);
      if (resumesData.length > 0) setResumeId(resumesData[0].resume_id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load job");
    } finally {
      setLoading(false);
    }
  }

  async function checkMatch() {
    if (!resumeId) return;
    setError("");
    try {
      const res = await api.matches.run(resumeId, jobId);
      const m = res.matches[0];
      if (m) {
        setScore(m.match_score);
        setGap(m.skill_gap);
      } else {
        setScore(0);
        setGap([]);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Matching failed");
    }
  }

  async function apply() {
    if (!resumeId) return;
    setApplying(true);
    setError("");
    try {
      await api.applications.create(jobId, resumeId);
      router.push("/applications");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to apply");
    } finally {
      setApplying(false);
    }
  }

  if (loading) {
    return (
      <div className="text-center py-16">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Loading job...</p>
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">{error}</div>
        <Link href="/jobs" className="text-indigo-600 hover:underline mt-4 inline-block">
          ← Back to Jobs
        </Link>
      </div>
    );
  }

  const required = job?.structured_requirements?.skills ?? [];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link href="/jobs" className="text-sm text-indigo-600 hover:underline">
        ← Back to Jobs
      </Link>

      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h1 className="text-2xl font-bold">{job?.title}</h1>
            <p className="text-gray-500">{job?.company} {job?.location ? `· ${job.location}` : ""}</p>
          </div>
          {score !== null && (
            <span className={`text-3xl font-bold ${score >= 70 ? "text-emerald-600" : score >= 40 ? "text-amber-600" : "text-rose-600"}`}>
              {score}%
            </span>
          )}
        </div>

        {job?.raw_description && (
          <p className="text-sm text-gray-600 mt-4 whitespace-pre-line">{job.raw_description}</p>
        )}

        {required.length > 0 && (
          <div className="mt-4">
            <h3 className="font-medium mb-2 text-sm">Required skills</h3>
            <div className="flex flex-wrap gap-2">
              {required.map((s, i) => (
                <span
                  key={i}
                  className={`text-xs px-2 py-1 rounded-full ${gap.includes(s) ? "bg-rose-100 text-rose-800" : "bg-indigo-100 text-indigo-800"}`}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {resumes.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border flex flex-col md:flex-row gap-4 md:items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Check match with resume</label>
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
          <div className="flex gap-2">
            <button
              onClick={checkMatch}
              className="border border-gray-300 px-4 py-2 rounded-lg text-sm hover:bg-gray-100"
            >
              Check Match
            </button>
            <button
              onClick={apply}
              disabled={applying}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
            >
              {applying ? "Applying..." : "Apply"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
