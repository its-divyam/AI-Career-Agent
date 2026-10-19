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
      request<{ user_id: string; email: string; access_token: string }>("/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    login: (email: string, password: string) =>
      request<{ user_id: string; email: string; access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
  },
  resume: {
    list: () =>
      request<{
        resume_id: string;
        target_role: string;
        ats_score: number;
        version: number;
        created_at: string | null;
      }[]>("/resumes"),
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
  },
  skillGap: {
    list: () =>
      request<{
        id: string;
        resume_id: string;
        target_role: string;
        have: string[];
        missing: string[];
        recommendations: { skill: string; project_idea: string; resource: string }[];
        created_at: string | null;
      }[]>("/skill-gap"),
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
  health: {
    check: () => request<{ status: string }>("/health"),
  },
  jobs: {
    list: () =>
      request<{
        job_id: string;
        source: string;
        title: string;
        company: string | null;
        location: string | null;
      }[]>("/jobs"),
    get: (id: string) =>
      request<{
        job_id: string;
        source: string;
        title: string;
        company: string | null;
        location: string | null;
        raw_description: string | null;
        structured_requirements: { skills?: string[] } | null;
      }>(`/jobs/${id}`),
  },
  matches: {
    list: () =>
      request<{
        match_id: string;
        job_id: string;
        title: string;
        company: string | null;
        location: string | null;
        match_score: number;
        match_reasons: string[];
        skill_gap: string[];
        created_at: string | null;
      }[]>("/matches"),
    run: (resumeId: string, jobId?: string, topN = 20) =>
      request<{
        status: string;
        matches: {
          job_id: string;
          title: string;
          company: string | null;
          match_score: number;
          match_reasons: string[];
          skill_gap: string[];
        }[];
      }>("/matches/run", {
        method: "POST",
        body: JSON.stringify({ resume_id: resumeId, job_id: jobId ?? null, top_n: topN }),
      }),
  },
  applications: {
    list: () =>
      request<{
        application_id: string;
        status: string;
        draft_resume: Record<string, unknown> | null;
        draft_cover_letter: string | null;
        job_id: string;
        job_title: string;
        company: string | null;
        created_at: string | null;
      }[]>("/applications"),
    create: (jobId: string, resumeId: string) =>
      request<{
        application_id: string;
        status: string;
        draft_resume: Record<string, unknown> | null;
        draft_cover_letter: string | null;
      }>("/applications", {
        method: "POST",
        body: JSON.stringify({ job_id: jobId, resume_id: resumeId }),
      }),
    update: (id: string, patch: { status?: string; draft_cover_letter?: string; draft_resume?: Record<string, unknown> }) =>
      request<{
        application_id: string;
        status: string;
        draft_resume: Record<string, unknown> | null;
        draft_cover_letter: string | null;
      }>(`/applications/${id}`, {
        method: "PATCH",
        body: JSON.stringify(patch),
      }),
  },
  tasks: {
    skillGap: (resumeId: string, targetRole: string) =>
      request<{
        task_id: string;
        status: string;
        result?: {
          have: string[];
          missing: string[];
          recommendations: { skill: string; project_idea: string; resource: string }[];
        };
        error?: string | null;
      }>("/tasks/skill-gap", {
        method: "POST",
        body: JSON.stringify({ resume_id: resumeId, target_role: targetRole }),
      }),
    status: (taskId: string) =>
      request<{
        task_id: string;
        status: string;
        result?: Record<string, unknown>;
        error?: string | null;
      }>(`/tasks/${taskId}`),
  },
};
