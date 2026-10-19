# Weekly Report — Week 2

**Project:** Skillgraph — An AI-Powered Career Assistant  
**Date Range:** 08 September 2026 – 14 September 2026  
**Author:** Divyam Garg and Khilika Garg
**Institution:** JIMS Greater Noida  

---

## 1. Executive Summary

During Week 2, Skillgraph was upgraded from a linear pipeline to an agentic system. The core work involved integrating **LangGraph** for multi-step analysis orchestration, **ChromaDB** for retrieval-augmented recommendations, **Alembic** for production-grade database migrations, and **Celery** with Redis for background task processing. The system was redesigned to support both synchronous and asynchronous execution paths, with a graceful fallback mechanism when background workers are unavailable.

By the end of Week 2, the system had grown from 9 to **14 API endpoints**, from **9 to 40 passing tests**, and featured a complete jobs pipeline with applications lifecycle management, background task processing, and a redesigned frontend with a redesigned landing page and branding (renamed to **Skillgraph**).

---

## 2. Objectives for Week 2

| # | Objective | Status |
|---|-----------|--------|
| 1 | Implement Alembic migrations with baseline and PostgreSQL readiness | ✅ Complete |
| 2 | Build RAG pipeline with ChromaDB and per-user isolation | ✅ Complete |
| 3 | Integrate LangGraph for analysis orchestration | ✅ Complete |
| 4 | Build jobs pipeline with deterministic matching and applications lifecycle | ✅ Complete |
| 5 | Implement Celery background tasks with sync fallback | ✅ Complete |
| 6 | Redesign frontend with jobs pages, applications tracker, and Skillgraph branding | ✅ Complete |
| 7 | Expand test suite and achieve full coverage | ✅ Complete |
| 8 | Add Docker Compose for multi-service deployment | ✅ Complete |

---

## 3. Technical Implementation

### 3.1 Database Migrations with Alembic

**Stage 1** introduced **Alembic** for schema version control. A migration baseline was created covering all 8 tables established in Week 1. The `env.py` was configured for async operation with SQLite batch mode, and a `compare_type=True` flag ensures schema changes are detected automatically.

#### Key Configuration

- **Migration baseline:** `a4f4540d1f2e`
- **Async support:** `async env.py` with `run_async=True`
- **PostgreSQL readiness:** `asyncpg` added to requirements; `DATABASE_URL` is environment-driven
- **Verification:** A fresh `alembic upgrade head` on a clean database reproduced the exact schema

### 3.2 Retrieval-Augmented Generation (RAG) with ChromaDB

**Stage 2** added a RAG pipeline using **ChromaDB** as the vector store and **Ollama** (`nomic-embed-text`) for embeddings.

#### Architecture

- **Embedding function:** `OllamaEmbeddingFunction` with an async wrapper (`ollama_embed`)
- **Chunking strategy:** 800-character chunks with 150-character overlap
- **Persistent storage:** Chroma client persists to `./data/chroma`
- **Per-user isolation:** Every index and query is namespaced by `user_id` + `resume_id`
- **Skill-gap integration:** Top-4 relevant chunks are retrieved and injected as context into the recommendation engine
- **Fallback mechanism:** When the LLM is unavailable, recommendations degrade gracefully with static, taxonomy-based suggestions

#### Verification

6 hermetic tests covering chunking, indexing/query roundtrip, and per-user isolation. All passed.

### 3.3 LangGraph Orchestration

**Stage 3** introduced **LangGraph** to orchestrate the analysis pipeline. The graph follows a three-stage flow:

1. **Retrieve** — Fetch skills and resume context
2. **ATS Scoring** — Compute compatibility scores
3. **Gap Analysis** — Identify missing skills and generate recommendations

#### Design Decisions

- **Quality gate:** Degenerate or low-confidence parses are routed to a manual review fallback
- **Retry mechanism:** The gap analysis node retries up to 2 times on failure
- **Zero-overlap guard:** Prevents redundant skill reporting across nodes
- **Parity verification:** Tests proved that graph output is identical to direct function calls, ensuring the graph is a pure orchestration layer with no logic rewriting

#### State Management

`CareerState` carries `user_id` and `resume_id` end-to-end through every node, ensuring per-user isolation is maintained throughout the graph execution.

### 3.4 Jobs Pipeline and Applications

**Stage 4** built a complete jobs pipeline:

#### Job Agent

- **Deterministic skill extraction:** Uses word-boundary-aware keyword extraction with guards for short names
- **Ambiguous exclusion:** Common false positives like "cv" and "gc" are excluded
- **Overlap scoring:** Matches candidate skills against job requirements with configurable weights
- **Seed data:** 6 demo jobs were seeded for immediate testing

#### Applications Lifecycle

Applications follow a strict lifecycle: `drafted` → `approved` → `applied` → `withdrawn`. Each status transition is validated, and all queries are filtered by `user_id`.

#### Job Matching Graph

A match graph scores each candidate job against the user's resume, ranks them, and persists the results. The `POST /matches` endpoint triggers the graph and returns ranked results.

### 3.5 Celery Background Processing

**Stage 5** added **Celery** with Redis as the task broker and result backend.

#### Key Design: Broker-Down Fallback

The most critical architectural decision was implementing a **broker-down fallback** pattern. A TCP pre-flight check (`_broker_reachable()`, 2-second timeout) determines whether Redis is available:

- **Broker up:** Tasks are enqueued → `POST /tasks/*` returns `202 Accepted` → client polls `GET /tasks/{id}`
- **Broker down:** Tasks run synchronously inline → `POST /tasks/*` returns `202` with `status: "SUCCESS"` and the result directly

This means the system degrades gracefully without errors when Redis is unavailable, while still exposing the full async contract.

#### Task Registration Fix

A `KeyError: 'career.match_jobs'` was encountered when tasks were enqueued but not registered by the worker. The fix was adding an explicit import of `analysis_tasks` in `app/tasks/__init__.py`, ensuring all task functions are discovered by the Celery app at startup.

#### Worker Configuration

- **Pool:** `solo` (required for Windows compatibility; `prefork` is not supported on Windows)
- **Timeouts:** Short socket/retry timeouts (2s) ensure dead brokers fail fast (~12.8s) rather than timing out after 109s
- **Services:** `docker-compose.yml` includes an `api`, `worker`, `db`, `redis`, and `ollama` service

#### Verification

Live end-to-end testing confirmed:
- `POST /tasks/skill-gap` → `202` with task ID (broker available)
- `POST /tasks/skill-gap` → `202` with `status: "SUCCESS"` and result (broker unavailable)
- `GET /tasks/{id}` returns ownership-checked status and result
- All 7 task tests pass

### 3.6 Frontend Redesign and Branding

**Stage 6** completed the frontend overhaul:

#### Branding

The application was renamed from "AI Career Agent" to **Skillgraph**, reflecting the underlying skill-graph architecture. A new logo was integrated, and the color scheme was updated to match the logo's palette (dark navy, orange, teal).

#### New Pages

| Page | Description |
|------|-------------|
| `/jobs` | Job catalog with resume picker, sync matching, and apply |
| `/jobs/[id]` | Job detail with required-skills chips, per-resume match score |
| `/applications` | Application tracker with drafted → approved → applied lifecycle |

#### Background Task Polling

A new `useTask` hook was created to support the background task pattern. The skill-gap page was converted to use this hook, displaying immediate results when running synchronously and polling every 2 seconds when a background worker is available.

#### Navigation

The `Nav.tsx` component was updated to display the Skillgraph logo and name, with updated link colors and button styles matching the new branding.

### 3.7 Docker Compose Deployment

A `docker-compose.yml` was created with five services:

| Service | Image | Purpose |
|---------|-------|---------|
| `api` | Python/FastAPI | Backend API |
| `worker` | Python/FastAPI | Celery background worker |
| `db` | PostgreSQL | Primary database |
| `redis` | Redis | Celery broker/backend |
| `ollama` | Ollama | LLM and embedding model serving |

### 3.8 Test Suite Expansion

The test suite grew from 9 to **40 tests** covering:

- ATS scoring, resume parsing, skill normalization
- RAG chunking, indexing, query, and per-user isolation
- LangGraph parity, retry logic, quality gate, and review fallback
- Job skill extraction, match scoring, endpoint CRUD, and per-user isolation
- Celery tasks, broker-down sync fallback, task ownership, and status queries

---

## 4. Challenges and Solutions

### Challenge 1: Task Registration on Worker Startup
**Problem:** Celery workers failed with `KeyError: 'career.match_jobs'` because task functions were defined but not imported at module load time.  
**Solution:** Added explicit `from app.tasks import analysis_tasks` to `app/tasks/__init__.py`, ensuring all tasks are registered before the worker starts accepting jobs.

### Challenge 2: Celery Pool Compatibility on Windows
**Problem:** The default `prefork` pool is incompatible with Windows due to lack of `fork` system call.  
**Solution:** Used `--pool=solo` for Windows development. The `docker-compose` configuration uses the default `prefork` pool for production Linux containers.

### Challenge 3: Broker-Down Error Handling
**Problem:** Without a fallback, a down Redis would cause all task endpoints to return 500 errors, breaking the user experience.  
**Solution:** Implemented TCP pre-flight check with short timeout, falling back to synchronous execution when the broker is unreachable.

### Challenge 4: Stale `.next` Build Cache
**Problem:** The Next.js dev server crashed with `ENOENT: no such file or directory` due to corrupted `.next` cache from concurrent server instances.  
**Solution:** Deleted `.next` directory, killed all orphaned processes, and restarted a single dev server instance.

---

## 5. Verification Metrics

| Metric | Value |
|--------|-------|
| Backend tests passing | **40 / 40** |
| API endpoints exposed | **14** |
| Database tables | 8 |
| Frontend pages | **11** |
| Background task routes | 2 (`/tasks/skill-gap`, `/tasks/matches`) |
| Docker services | 5 (api, worker, db, redis, ollama) |
| Celery tasks registered | 2 (`analyze_resume`, `match_jobs`) |
| Build status | ✅ Clean (`next build` — 11 routes) |
| Auth method | JWT + bcrypt |
| LLM model | llama3.2 + nomic-embed-text (Ollama) |
| Vector store | ChromaDB (persistent) |
| Migration tool | Alembic (baseline `a4f4540d1f2e`) |
| Task fallback | Broker-down sync execution |

---

## 6. Summary and Look Ahead

Week 2 transformed Skillgraph from a linear pipeline into a production-grade agentic system. The integration of LangGraph, ChromaDB, Celery, and Alembic provided the architectural backbone for a scalable, maintainable platform. The complete jobs pipeline, applications lifecycle, and background task processing were verified end-to-end.

**Future work:** Production hardening — external job source integration (Adzuna/JSearch), LLM-tailored resume and cover letter drafting with human approval gates, weekly progress reports via Celery Beat, CI/CD pipeline setup, rate limiting, and monitoring.

---

*Report generated for academic review.*
