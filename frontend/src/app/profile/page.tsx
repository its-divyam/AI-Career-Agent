"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

interface Profile {
  id: string;
  user_id: string;
  email: string;
  display_name: string | null;
  target_role: string | null;
  location: string | null;
  bio: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  total_resumes: number;
  total_skill_gaps: number;
  total_applications: number;
  total_skills_learned: number;
  best_ats_score: number | null;
  recent_activity: { items: { type: string; description: string; timestamp: string }[] } | null;
  skill_progress: Record<string, { computed: number; skills_missing: number }> | null;
  member_since: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    display_name: "",
    target_role: "",
    location: "",
    bio: "",
    linkedin_url: "",
    github_url: "",
    portfolio_url: "",
  });

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadProfile() {
    setLoading(true);
    try {
      const data = await api.profile.get();
      setProfile(data);
      setForm({
        display_name: data.display_name || "",
        target_role: data.target_role || "",
        location: data.location || "",
        bio: data.bio || "",
        linkedin_url: data.linkedin_url || "",
        github_url: data.github_url || "",
        portfolio_url: data.portfolio_url || "",
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load profile");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const data = await api.profile.update(form);
      setProfile(data);
      setEditing(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
    } finally {
      setSaving(false);
    }
  }

  function getActivityIcon(type: string) {
    switch (type) {
      case "resume": return "📄";
      case "skill_gap": return "🎯";
      case "application": return "📝";
      default: return "📌";
    }
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString("en-US", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Loading profile...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16">
        <p className="text-gray-500">Profile not found.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Profile</h1>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
          >
            Edit Profile
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Profile Card */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        {editing ? (
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Display Name</label>
                <input
                  value={form.display_name}
                  onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Target Role</label>
                <input
                  value={form.target_role}
                  onChange={(e) => setForm({ ...form, target_role: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                  placeholder="e.g. AI Engineer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Location</label>
                <input
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                  placeholder="e.g. San Francisco, CA"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">LinkedIn URL</label>
                <input
                  value={form.linkedin_url}
                  onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                  placeholder="https://linkedin.com/in/..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">GitHub URL</label>
                <input
                  value={form.github_url}
                  onChange={(e) => setForm({ ...form, github_url: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                  placeholder="https://github.com/..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Portfolio URL</label>
                <input
                  value={form.portfolio_url}
                  onChange={(e) => setForm({ ...form, portfolio_url: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2"
                  placeholder="https://..."
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Bio</label>
              <textarea
                value={form.bio}
                onChange={(e) => setForm({ ...form, bio: e.target.value })}
                className="w-full border rounded-lg px-3 py-2"
                rows={3}
                placeholder="Tell us about yourself..."
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={saving}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="border border-gray-300 px-4 py-2 rounded-lg text-sm hover:bg-gray-100"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center text-2xl font-bold text-indigo-600">
                {(profile.display_name || profile.email)[0].toUpperCase()}
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold">{profile.display_name || "No name set"}</h2>
                <p className="text-gray-500">{profile.email}</p>
                {profile.location && (
                  <p className="text-sm text-gray-500 mt-1">📍 {profile.location}</p>
                )}
              </div>
            </div>

            {profile.bio && (
              <p className="text-gray-600 text-sm">{profile.bio}</p>
            )}

            {profile.target_role && (
              <div className="inline-block bg-indigo-100 text-indigo-800 text-sm px-3 py-1 rounded-full">
                🎯 Target: {profile.target_role}
              </div>
            )}

            <div className="flex gap-4 text-sm">
              {profile.linkedin_url && (
                <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                  LinkedIn →
                </a>
              )}
              {profile.github_url && (
                <a href={profile.github_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                  GitHub →
                </a>
              )}
              {profile.portfolio_url && (
                <a href={profile.portfolio_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                  Portfolio →
                </a>
              )}
            </div>

            <p className="text-xs text-gray-400">
              Member since {formatDate(profile.member_since)}
            </p>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <p className="text-2xl font-bold text-indigo-600">{profile.total_resumes}</p>
          <p className="text-xs text-gray-500">Resumes</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <p className="text-2xl font-bold text-emerald-600">{profile.total_skill_gaps}</p>
          <p className="text-xs text-gray-500">Skill Gaps Analyzed</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <p className="text-2xl font-bold text-amber-600">{profile.total_applications}</p>
          <p className="text-xs text-gray-500">Applications</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <p className="text-2xl font-bold text-rose-600">{profile.best_ats_score ?? "—"}</p>
          <p className="text-xs text-gray-500">Best ATS Score</p>
        </div>
      </div>

      {/* Skill Progress */}
      {profile.skill_progress && Object.keys(profile.skill_progress).length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="font-semibold mb-4">Skill Progress by Role</h3>
          <div className="space-y-3">
            {Object.entries(profile.skill_progress).map(([role, data]) => (
              <div key={role} className="flex items-center justify-between">
                <span className="text-sm font-medium">{role}</span>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">{data.computed} analyses</span>
                  <span className="text-xs text-rose-600">{data.skills_missing} gaps remaining</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h3 className="font-semibold mb-4">Recent Activity</h3>
        {profile.recent_activity?.items?.length ? (
          <div className="space-y-3">
            {profile.recent_activity.items.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-lg">{getActivityIcon(item.type)}</span>
                <div className="flex-1">
                  <p className="text-sm">{item.description}</p>
                  <p className="text-xs text-gray-400">{formatDate(item.timestamp)}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No activity yet. Upload a resume to get started!</p>
        )}
      </div>
    </div>
  );
}
