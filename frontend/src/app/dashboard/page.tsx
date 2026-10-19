"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

interface Resume {
  resume_id: string;
  target_role: string;
  ats_score: number;
  version: number;
  created_at: string | null;
}

interface SkillGap {
  id: string;
  resume_id: string;
  target_role: string;
  have: string[];
  missing: string[];
  created_at: string | null;
}

export default function DashboardPage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [skillGaps, setSkillGaps] = useState<SkillGap[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [resumesData, gapsData] = await Promise.all([
        api.resume.list(),
        api.skillGap.list(),
      ]);
      setResumes(resumesData);
      setSkillGaps(gapsData);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }

  function formatDate(iso: string | null) {
    if (!iso) return "—";
    return new Date(iso).toLocaleDateString("en-US", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
  }

  function getBestAts() {
    if (resumes.length === 0) return "—";
    return Math.max(...resumes.map((r) => r.ats_score ?? 0));
  }

  if (loading) {
    return (
      <div className="text-center py-16">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link
          href="/upload"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
        >
          + Upload Resume
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm border text-center">
          <p className="text-3xl font-bold text-indigo-600">{resumes.length}</p>
          <p className="text-sm text-gray-500">Resumes Uploaded</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border text-center">
          <p className="text-3xl font-bold text-emerald-600">{skillGaps.length}</p>
          <p className="text-sm text-gray-500">Skill Gaps Analyzed</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border text-center">
          <p className="text-3xl font-bold text-amber-600">{getBestAts()}</p>
          <p className="text-sm text-gray-500">Best ATS Score</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border text-center">
          <p className="text-3xl font-bold text-rose-600">
            {skillGaps.reduce((sum, g) => sum + (g.missing?.length ?? 0), 0)}
          </p>
          <p className="text-sm text-gray-500">Total Gaps Found</p>
        </div>
      </div>

      {/* Resumes Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="font-semibold">Resumes</h2>
        </div>
        {resumes.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500 mb-4">No resumes uploaded yet.</p>
            <Link href="/upload" className="text-indigo-600 hover:underline font-medium">
              Upload your first resume →
            </Link>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Target Role</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">ATS Score</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Uploaded</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {resumes.map((r) => (
                <tr key={r.resume_id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm">{r.target_role}</td>
                  <td className="px-6 py-3">
                    <span className={`text-sm font-medium ${(r.ats_score ?? 0) >= 70 ? "text-emerald-600" : (r.ats_score ?? 0) >= 50 ? "text-amber-600" : "text-rose-600"}`}>
                      {r.ats_score ?? "—"}/100
                    </span>
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-500">{formatDate(r.created_at)}</td>
                  <td className="px-6 py-3">
                    <Link
                      href={`/skill-gap?resume_id=${r.resume_id}&role=${encodeURIComponent(r.target_role)}`}
                      className="text-indigo-600 text-sm hover:underline"
                    >
                      Analyze Skills
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Skill Gaps */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="font-semibold">Recent Skill Gap Analyses</h2>
        </div>
        {skillGaps.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500">No skill gap analyses yet. Upload a resume first.</p>
          </div>
        ) : (
          <div className="divide-y">
            {skillGaps.map((gap) => (
              <div key={gap.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{gap.target_role}</span>
                  <span className="text-xs text-gray-400">{formatDate(gap.created_at)}</span>
                </div>
                <div className="flex gap-4 text-xs">
                  <span className="text-emerald-600">{gap.have?.length ?? 0} skills matched</span>
                  <span className="text-rose-600">{gap.missing?.length ?? 0} gaps found</span>
                </div>
                {gap.missing && gap.missing.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {gap.missing.slice(0, 5).map((skill, i) => (
                      <span key={i} className="bg-rose-100 text-rose-700 text-xs px-2 py-0.5 rounded-full">
                        {skill}
                      </span>
                    ))}
                    {gap.missing.length > 5 && (
                      <span className="text-xs text-gray-400">+{gap.missing.length - 5} more</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
