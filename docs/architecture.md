# Architecture

## 1. High-level overview

```
                    USER
                      |
                Career Agent (orchestrator, LangGraph)
                      |
       +--------------+--------------+
       |              |              |
 Resume Agent   Job Researcher   Skill Agent
       |              |              |
 Resume Score   Job Matching    Skill Gap
       +--------------+--------------+
                      |
                Application Agent
                      |
                Human Approval
                      |
                Apply / Track
```

The orchestrator is a **stateful graph**, not a linear chain — it needs to branch (e.g. re-run skill-gap analysis when a new job is selected) and loop (e.g. regenerate a cover letter after user edits). This is why LangGraph is used instead of a plain LangChain sequential chain.

## 2. Components

### 2.1 Career Agent (orchestrator)
- Implemented as a LangGraph `StateGraph`.
- Holds shared state: user profile, resume data, job shortlist, skill gaps, draft applications, approval status.
- Routes to sub-agents based on the current state and the user's action (e.g. "analyze my resume" → Resume Agent node; "find jobs" → Job Researcher node).
- Persists state via LangGraph checkpointing so a session can be resumed later.

### 2.2 Resume Agent
- **Input:** raw resume file (PDF/DOCX)
- **Process:** text extraction (`pdfplumber` / `python-docx`) → LLM structuring pass (JSON schema: contact info, skills, experience, projects, education) → ATS-compatibility scoring (keyword density, section structure, formatting checks)
- **Output:** structured resume object + ATS score, written to the database and embedded into the vector store

### 2.3 Job Researcher Agent
- **Input:** target role, structured resume, optional filters (location, seniority)
- **Process:**
  1. Query job source (API-based: Adzuna / JSearch) for postings matching the role
  2. LLM-structure each JD into requirements (must-have skills, nice-to-have, seniority, tools)
  3. Compute similarity between resume embedding and JD embedding (vector search)
  4. LLM re-ranks the top candidates for nuance (e.g. weighting recency of experience)
- **Output:** ranked job list with structured requirements attached

### 2.4 Skill Agent
- **Input:** structured resume + one or more job requirement sets
- **Process:** set-difference between resume skills and job requirements, normalized against a canonical skills taxonomy; updates a **persistent skill profile** per user rather than recomputing from zero each time
- **Output:** skill gap report + project/resource recommendations (LLM-generated, grounded via few-shot examples to avoid inventing resources)

### 2.5 Application Agent
- **Input:** selected job, structured resume, career knowledge base
- **Process:** RAG retrieval of relevant past projects/achievements from the vector store → LLM drafts a reordered resume (surfacing the most relevant bullets) and a tailored cover letter
- **Output:** draft application package, status = `drafted`

### 2.6 Human Approval
- A UI checkpoint, not an agent. The user reviews/edits the draft before it can move to `approved`. No component in the system is permitted to skip this step.

### 2.7 Apply & Track
- On approval, the system logs the application (status = `approved` → `applied` once the user confirms submission) and opens the actual job posting for the user to submit manually, or submits via API where a legitimate, ToS-compliant submission API exists.
- A scheduled job (Celery) aggregates tracker + knowledge base data weekly into a progress report.

## 3. Data flow summary

1. Resume + target role in → Resume Agent structures it → stored in Postgres + embedded in vector store
2. Job Researcher pulls and structures postings → embedded and ranked against resume
3. Skill Agent computes gaps per top matches → updates persistent skill profile
4. User selects a job → Application Agent drafts a tailored package using RAG over the knowledge base
5. Human approves/edits → tracked → weekly report generated from accumulated data

## 4. Tech stack

| Layer | Choice | Rationale |
|---|---|---|
| Agent orchestration | LangGraph | Stateful, branching, resumable agent flows |
| Backend API | FastAPI | Async-native, integrates cleanly with LangGraph |
| Frontend | Next.js | SSR dashboard, matches existing stack |
| Background jobs | Celery + Redis | Scheduled reports, async job-search polling |
| Vector store | Chroma or Qdrant | Self-hostable, free, fits local-first dev pattern |
| LLM (dev) | Ollama (Llama 3.2/3.3) | Free local inference during development |
| LLM (prod) | Hosted API (e.g. Claude) for generation-heavy tasks | Higher quality for cover letters, nuanced ranking |
| Relational DB | PostgreSQL + Prisma | Structured data: users, resumes, jobs, applications |
| Job data source | Adzuna / JSearch API | ToS-compliant, avoids scraping legal risk |
| Resume parsing | `pdfplumber` + LLM structuring | More robust than regex-based parsing |

## 5. Scaling considerations

- **Cost:** cache embeddings; use a cheap/local model for extraction and parsing, reserve the stronger hosted model for generation tasks (cover letters, ranking nuance).
- **Concurrency:** move from local Ollama to a hosted inference API once concurrent users exceed what a single local queue can handle.
- **Rate limits:** job-source APIs need caching and backoff/retry; avoid re-fetching the same postings repeatedly.
- **State:** LangGraph checkpoint store should move from in-memory/SQLite (dev) to Postgres-backed checkpointing (prod) so agent sessions survive restarts.
- **Horizontal scaling:** FastAPI workers and Celery workers scale independently behind a load balancer; the vector store and Postgres are the shared state layer.

## 6. Failure modes to design around

- LLM hallucinating job requirements or resources → mitigate with grounded few-shot prompts and, where possible, retrieval-based grounding instead of open generation.
- Job source API downtime → cache last-known postings, degrade gracefully rather than failing the whole pipeline.
- Resume parsing errors on unusual formats → always show the user the parsed structure for confirmation before it feeds downstream agents.
