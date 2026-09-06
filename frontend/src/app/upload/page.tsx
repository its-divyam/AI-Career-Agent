"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

interface UploadResult {
  resume_id: string;
  parsed: Record<string, unknown>;
  ats_score: number;
  ats_flags: string[];
}

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("");
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
      setError("");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !targetRole) return;

    if (!isLoggedIn()) {
      setError("Please login first");
      router.push("/login");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const res = await api.resume.upload(file, targetRole);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  function handleAnalyzeSkillGap() {
    if (result) {
      router.push(`/skill-gap?resume_id=${result.resume_id}&role=${encodeURIComponent(targetRole)}`);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Upload Resume</h1>

      <form onSubmit={handleUpload} className="space-y-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
            isDragActive ? "border-indigo-500 bg-indigo-50" : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input {...getInputProps()} />
          {file ? (
            <div>
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          ) : (
            <div>
              <p className="text-gray-500">Drag & drop your resume here, or click to select</p>
              <p className="text-xs text-gray-400 mt-1">PDF or DOCX, max 10MB</p>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Target Role</label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. AI Engineer, Software Engineer, Data Scientist"
            className="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={!file || !targetRole || loading}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? "Analyzing resume..." : "Upload & Analyze"}
        </button>
      </form>

      {result && (
        <div className="mt-8 bg-white p-6 rounded-xl shadow-sm border space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Analysis Results</h2>
            <span className="text-2xl font-bold text-indigo-600">{result.ats_score}/100</span>
          </div>

          <div>
            <h3 className="font-medium mb-2">Detected Skills</h3>
            <div className="flex flex-wrap gap-2">
              {(result.parsed.skills as string[] || []).map((skill, i) => (
                <span key={i} className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {result.ats_flags.length > 0 && (
            <div>
              <h3 className="font-medium mb-2">ATS Flags</h3>
              <ul className="space-y-1">
                {result.ats_flags.map((flag, i) => (
                  <li key={i} className="text-sm text-amber-700 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full inline-block" />
                    {flag}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={handleAnalyzeSkillGap}
            className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700"
          >
            Analyze Skill Gap →
          </button>
        </div>
      )}
    </div>
  );
}
