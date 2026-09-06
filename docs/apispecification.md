# API Specification

Base URL: `/api/v1`
Framework: FastAPI. All authenticated endpoints require a bearer token (see `security.md`).

## 1. Auth

### POST /auth/signup
Body: `{ "email": string, "password": string }`
Response: `201 { "user_id": uuid }`

### POST /auth/login
Body: `{ "email": string, "password": string }`
Response: `200 { "access_token": string, "token_type": "bearer" }`

## 2. Resume

### POST /resumes
Multipart upload. Triggers the Resume Agent.
Body: file (PDF/DOCX), `target_role: string`
Response:
```json
{
  "resume_id": "uuid",
  "parsed": { "skills": [...], "experience": [...], "projects": [...] },
  "ats_score": 78,
  "ats_flags": ["missing quantified achievements", "no summary section"]
}
```

### GET /resumes/{resume_id}
Returns the stored parsed resume.

### PATCH /resumes/{resume_id}
Body: corrected fields from the user (used when the parse needs manual fixes before downstream agents run).

## 3. Skill gap

### POST /skill-gap
Triggers the Skill Agent for a given resume + target role (or a specific job, see below).
Body: `{ "resume_id": "uuid", "target_role": string }`
Response:
```json
{
  "have": ["Python", "TensorFlow"],
  "missing": ["RAG", "LangGraph", "Docker"],
  "recommendations": [
    { "skill": "Docker", "project_idea": "...", "resource": "..." }
  ]
}
```

## 4. Job search

### POST /jobs/search
Triggers the Job Researcher Agent.
Body: `{ "resume_id": "uuid", "target_role": string, "location": string, "filters": {...} }`
Response: `202 { "job_search_id": "uuid" }` (async — job search + structuring can take several seconds; poll or use the status endpoint)

### GET /jobs/search/{job_search_id}
Response:
```json
{
  "status": "complete",
  "matches": [
    {
      "job_id": "uuid",
      "title": "AI Engineer",
      "company": "...",
      "match_score": 0.82,
      "match_reasons": ["Strong Python/ML overlap", "Missing: RAG experience"],
      "skill_gap": ["RAG", "LangGraph"]
    }
  ]
}
```

### GET /jobs/{job_id}
Returns full structured job details.

## 5. Applications

### POST /applications
Triggers the Application Agent to draft a tailored package.
Body: `{ "resume_id": "uuid", "job_id": "uuid" }`
Response:
```json
{
  "application_id": "uuid",
  "status": "drafted",
  "draft_resume": {...},
  "draft_cover_letter": "..."
}
```

### PATCH /applications/{application_id}
User edits to the draft before approval.
Body: `{ "draft_cover_letter": string, "draft_resume": {...} }`

### POST /applications/{application_id}/approve
The human approval gate. No downstream action can occur without this call.
Response: `200 { "status": "approved" }`

### POST /applications/{application_id}/mark-applied
Called after the user manually submits (or after a compliant submit API confirms).
Response: `200 { "status": "applied", "applied_at": timestamp }`

### GET /applications
Query params: `status`, `job_id`. Returns the tracker list for the dashboard/kanban view.

## 6. Progress reports

### GET /reports/weekly/latest
Returns the most recent auto-generated report.

### GET /reports/weekly?week_start=2026-08-31
Returns a specific week's report.

## 7. Agent orchestration (internal/debug)

### GET /agent-runs?user_id=...
For debugging and audit — returns recent agent run summaries (not full prompts/PII), used to diagnose failures without exposing raw LLM traffic.

## 8. Error format

All errors follow:
```json
{ "error": { "code": "string", "message": "string" } }
```
Common codes: `INVALID_RESUME_FORMAT`, `JOB_SOURCE_UNAVAILABLE`, `APPROVAL_REQUIRED`, `RATE_LIMITED`.

## 9. Rate limiting

Job search and application-drafting endpoints are rate-limited per user (e.g. 20 job searches/hour, 30 draft generations/hour) to control LLM cost and respect upstream job-API limits. See `security.md` for enforcement details.
