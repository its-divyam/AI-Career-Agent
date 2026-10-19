# Skillgraph

An AI-powered career assistant that parses resumes, identifies skill gaps against target roles, and provides personalized project/resource recommendations — all with a human-in-the-loop approach.

## Features

- **Resume Upload & Parsing** — PDF/DOCX upload with LLM-powered structured extraction (skills, experience, projects, education) and ATS compatibility scoring
- **Skill Gap Analysis** — Compares your resume against a target role's requirements using a canonical skills taxonomy (63+ skills, 7 role presets)
- **Personalized Recommendations** — Project ideas and learning resources grounded in your specific skill gaps
- **Job Matching** — Deterministic skill-overlap scoring against an ingested job catalog, persisted per user
- **Applications** — Draft → approve → apply → withdraw lifecycle with timestamps
- **Background Tasks** — Celery-powered async analysis/matching with 202 + poll contract and automatic sync fallback when Redis is down
- **JWT Authentication** — Secure signup/login with bcrypt password hashing

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Database | SQLite (local dev) / PostgreSQL (production) |
| Frontend | Next.js 15, React 19, Tailwind CSS |
| Auth | JWT (python-jose), bcrypt |
| Resume Parsing | pdfplumber, python-docx, Ollama (LLM) |
| Agents | LangGraph (analysis + matching graphs), ChromaDB RAG |
| Background Jobs | Celery + Redis (with sync fallback) |
| Migrations | Alembic |
| Testing | pytest, pytest-asyncio |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) (optional, for LLM-powered resume parsing)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not already created)
python -m venv ../venv
../venv/Scripts/activate        # Windows
# source ../venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database and seed skills
python init_db.py
python seed_skills.py

# Start the API server (port 8001)
.\start.ps1                    # Windows (auto-kills port conflicts)
# uvicorn app.main:app --reload --port 8001   # manual start
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Open

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/signup` | No | Create account (auto-creates profile) |
| `POST` | `/api/v1/auth/login` | Yes | Login, get JWT token |
| `GET` | `/api/v1/profile` | Yes | Get user profile with activity stats |
| `PATCH` | `/api/v1/profile` | Yes | Update profile (name, bio, links, etc.) |
| `POST` | `/api/v1/resumes` | Yes | Upload resume (PDF/DOCX) |
| `GET` | `/api/v1/resumes` | Yes | List your resumes |
| `GET` | `/api/v1/resumes/{id}` | Yes | Get parsed resume |
| `PATCH` | `/api/v1/resumes/{id}` | Yes | Update resume fields |
| `POST` | `/api/v1/skill-gap` | Yes | Compute skill gap for target role (LangGraph) |
| `GET` | `/api/v1/skill-gap` | Yes | List past gap analyses |
| `POST` | `/api/v1/jobs/ingest` | Yes | Ingest a job posting |
| `GET` | `/api/v1/jobs` | Yes | List jobs |
| `GET` | `/api/v1/jobs/{id}` | Yes | Job detail + requirements |
| `POST` | `/api/v1/matches/run` | Yes | Score jobs against a resume |
| `GET` | `/api/v1/matches` | Yes | List your matches (score-ordered) |
| `POST` | `/api/v1/applications` | Yes | Create application draft |
| `GET` | `/api/v1/applications` | Yes | List your applications |
| `PATCH` | `/api/v1/applications/{id}` | Yes | Update drafts / lifecycle status |
| `POST` | `/api/v1/tasks/skill-gap` | Yes | Async gap analysis (202 + poll) |
| `POST` | `/api/v1/tasks/matches` | Yes | Async matching (202 + poll) |
| `GET` | `/api/v1/tasks/{id}` | Yes | Task status (ownership-checked) |
| `GET` | `/health` | No | Health check |

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page with feature overview |
| `/register` | Create account |
| `/login` | Login |
| `/upload` | Drag-and-drop resume upload with ATS scoring |
| `/skill-gap` | Side-by-side have/missing skills with recommendations (background task + polling) |
| `/dashboard` | Overview with stats and resume table |
| `/jobs` | Job catalog + resume matching |
| `/jobs/[id]` | Job detail, match check, apply |
| `/applications` | Application tracker with lifecycle actions |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route handlers
│   │   │   ├── auth.py       # Signup/login
│   │   │   ├── resume.py     # Resume upload/parse (+ RAG indexing)
│   │   │   ├── skill_gap.py  # Skill gap via LangGraph
│   │   │   ├── jobs.py       # Ingest, list, match runs
│   │   │   ├── applications.py # Application lifecycle
│   │   │   ├── task_routes.py  # Async 202 + poll surface
│   │   │   └── health.py     # Health check
│   │   ├── agents/           # Core AI logic
│   │   │   ├── resume_agent.py   # PDF/DOCX parsing + LLM structuring
│   │   │   ├── skill_agent.py    # Skill normalization + gap analysis
│   │   │   └── job_agent.py      # Job skill extraction + match scoring
│   │   ├── graph/            # LangGraph pipelines
│   │   │   ├── runner.py     # Analysis graph (retrieve → ATS → gap)
│   │   │   ├── match_runner.py # Matching graph (score → rank)
│   │   │   └── nodes.py      # Retry + quality-gate routing
│   │   ├── rag/              # ChromaDB retrieval (per-user isolated)
│   │   ├── services/         # Shared by sync routes + Celery tasks
│   │   ├── tasks/            # Celery app + background tasks
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── skill.py      # Skills, UserSkill, SkillGapResult
│   │   │   ├── job.py        # Job, JobMatch
│   │   │   ├── application.py
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── utils/
│   │       ├── auth.py       # JWT + bcrypt
│   │       └── dependencies.py   # Auth dependency
│   ├── tests/                # 40 passing tests
│   ├── migrations/           # Alembic (baseline: user-isolation schema)
│   ├── init_db.py            # Create all tables (dev convenience)
│   ├── seed_skills.py        # Seed 63 canonical skills
│   ├── seed_jobs.py          # Seed 6 demo jobs
│   ├── start.ps1             # Start script (auto-frees port)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/              # Next.js App Router pages
│       │   ├── page.tsx          # Landing
│       │   ├── layout.tsx        # Root layout + nav
│       │   ├── upload/page.tsx   # Resume upload
│       │   ├── skill-gap/page.tsx # Gap analysis
│       │   ├── dashboard/page.tsx # Dashboard
│       │   ├── jobs/page.tsx     # Job catalog + matching
│       │   ├── jobs/[id]/page.tsx # Job detail + apply
│       │   ├── applications/page.tsx # Application tracker
│       │   ├── login/page.tsx     # Login
│       │   └── register/page.tsx  # Register
│       └── lib/
│           ├── api.ts        # API client (all endpoints)
│           ├── auth.ts       # Token management
│           └── useTask.ts    # Background-task polling hook
├── docs/                     # Project documentation
│   ├── project.md            # Problem statement & vision
│   ├── architecture.md       # System design
│   ├── apispecification.md   # API contract
│   ├── databasedesign.md     # Schema design
│   ├── security.md           # Security design
│   ├── testing.md            # Testing strategy
│   ├── deployment.md         # Deployment plan
│   └── webui.md              # UI/UX design
├── docker-compose.yml        # Full stack (Postgres, Redis, Ollama, API, Web)
└── README.md
```

## Testing

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Tests cover:
# - ATS score computation (full vs minimal resume)
# - Resume text extraction fallback
# - Skill normalization (aliases like "tf" → "TensorFlow")
# - Skill gap computation (partial and full skill sets)
# - Role-based skill requirements
# - RAG chunking, indexing/query roundtrip, per-user isolation
# - LangGraph parity with direct calls, retry, review fallback, quality gate
# - Job skill extraction + match scoring math
# - Jobs/matches/applications endpoints + per-user isolation
# - Celery tasks, broker-down sync fallback, task ownership
```

## Database

Uses SQLite for local development (zero setup). Schema changes go through
Alembic — never delete the `.db` file:

```bash
cd backend
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
```

Switch to PostgreSQL by updating `DATABASE_URL` in `backend/.env`:

```
DATABASE_URL=sqlite+aiosqlite:///./career_agent.db          # default (local)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db  # production
```

### Tables

| Table | Purpose |
|-------|---------|
| `users` | Auth credentials |
| `resumes` | Uploaded resumes with parsed JSON + ATS scores |
| `skills` | Canonical skills taxonomy (63 seeded) |
| `user_skills` | Skills extracted from user resumes |
| `skill_gap_results` | Computed gap analyses |
| `jobs` | Job postings catalog |
| `job_matches` | Match scores per user per job |
| `applications` | Application drafts with lifecycle status |

## Configuration

Environment variables in `backend/.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./career_agent.db
JWT_SECRET_KEY=change-me-in-production
LLM_PROVIDER=ollama           # ollama or hosted
LLM_MODEL=llama3.2            # model name
LLM_BASE_URL=http://localhost:11434
EMBED_MODEL=nomic-embed-text  # Ollama embedding model for RAG
RAG_TOP_K=4                   # retrieved chunks per query
REDIS_URL=redis://localhost:6379/0   # Celery broker/backend
CHROMA_PERSIST_DIR=./data/chroma
```

### Background worker (production / docker compose)

```bash
docker compose up -d redis db ollama
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
# Windows local dev (no prefork support):
celery -A app.tasks.celery_app worker --pool=solo --loglevel=info
```

Without Redis, task routes automatically run the same work synchronously.

## Roadmap

### Phase 1 (Done) — MVP Linear Pipeline
- [x] Resume upload + parsing
- [x] Skill normalization + gap analysis
- [x] JWT authentication + per-user isolation
- [x] Full frontend (upload, gap analysis, dashboard, auth)

### Phase 2 (Done) — Agentic System
- [x] Alembic migrations (baseline) + Postgres readiness (asyncpg, env-driven URL)
- [x] ChromaDB RAG with per-user isolation + grounded recommendations (fallback-safe)
- [x] LangGraph analysis graph (retrieve → ATS → gap, retry + quality gate) with parity tests
- [x] Jobs pipeline: ingest, deterministic matching engine, match graph, applications lifecycle
- [x] Celery background tasks (202 + poll, broker-down sync fallback, ownership-checked status)
- [x] Frontend: jobs catalog/detail, applications tracker, background-task polling on skill-gap

### Phase 3 — Production hardening (future)
- [ ] External job source integration (Adzuna/JSearch)
- [ ] LLM-tailored resume + cover letter drafting with human approval gate
- [ ] Weekly progress reports (Celery beat)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Rate limiting + monitoring

## License

MIT
