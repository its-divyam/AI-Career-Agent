"use client";

import { useState, useEffect } from "react";
import { isLoggedIn } from "@/lib/auth";

interface Resume {
  resume_id: string;
  target_role: string;
  ats_score: number;
  version: number;
}

export default function DashboardPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    setLoggedIn(isLoggedIn());
  }, []);

  if (!loggedIn) {
    return (
      <div className="max-w-2xl mx-auto text-center mt-16">
        <p className="text-gray-500 mb-4">Please login to view your dashboard.</p>
        <a href="/login" className="text-indigo-600 hover:underline">
          Login
        </a>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <a
          href="/upload"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
        >
          + Upload Resume
        </a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <p className="text-sm text-gray-500">Resumes Uploaded</p>
          <p className="text-3xl font-bold text-indigo-600">{resumes.length}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <p className="text-sm text-gray-500">Applications</p>
          <p className="text-3xl font-bold text-indigo-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <p className="text-sm text-gray-500">Skill Gaps Closed</p>
          <p className="text-3xl font-bold text-emerald-600">0</p>
        </div>
      </div>

      {resumes.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm border text-center">
          <p className="text-gray-500 mb-4">No resumes uploaded yet.</p>
          <a
            href="/upload"
            className="text-indigo-600 hover:underline font-medium"
          >
            Upload your first resume →
          </a>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Target Role</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">ATS Score</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Version</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {resumes.map((r) => (
                <tr key={r.resume_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm">{r.target_role}</td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium">{r.ats_score}/100</span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">v{r.version}</td>
                  <td className="px-4 py-3">
                    <a
                      href={`/skill-gap?resume_id=${r.resume_id}&role=${encodeURIComponent(r.target_role)}`}
                      className="text-indigo-600 text-sm hover:underline"
                    >
                      View Skills
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
