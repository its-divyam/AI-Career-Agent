const API_BASE = "/api/v1";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers["Content-Type"]
  ) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(err.error?.message || "Request failed");
  }

  return res.json();
}

export const api = {
  auth: {
    signup: (email: string, password: string) =>
      request<{ user_id: string; access_token: string }>("/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    login: (email: string, password: string) =>
      request<{ user_id: string; access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
  },
  resume: {
    upload: (file: File, targetRole: string) => {
      const form = new FormData();
      form.append("file", file);
      form.append("target_role", targetRole);
      return request<{
        resume_id: string;
        parsed: Record<string, unknown>;
        ats_score: number;
        ats_flags: string[];
      }>("/resumes", { method: "POST", body: form });
    },
    get: (id: string) =>
      request<{
        resume_id: string;
        parsed: Record<string, unknown>;
        ats_score: number;
        target_role: string;
        version: number;
      }>(`/resumes/${id}`),
    patch: (id: string, data: { parsed_json?: Record<string, unknown>; target_role?: string }) =>
      request<{ resume_id: string; updated: boolean }>(`/resumes/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
  },
  skillGap: {
    compute: (resumeId: string, targetRole: string) =>
      request<{
        have: string[];
        missing: string[];
        recommendations: { skill: string; project_idea: string; resource: string }[];
      }>("/skill-gap", {
        method: "POST",
        body: JSON.stringify({ resume_id: resumeId, target_role: targetRole }),
      }),
  },
  profile: {
    get: () =>
      request<{
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
      }>("/profile"),
    update: (data: {
      display_name?: string;
      target_role?: string;
      location?: string;
      bio?: string;
      linkedin_url?: string;
      github_url?: string;
      portfolio_url?: string;
    }) =>
      request<{
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
      }>("/profile", {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
  },
  health: {
    check: () => request<{ status: string }>("/health"),
  },
};
