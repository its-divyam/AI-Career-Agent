# AI Career Agent

An AI-powered career assistant that parses resumes, identifies skill gaps against target roles, and provides personalized project/resource recommendations — all with a human-in-the-loop approach.

## Features

- **Resume Upload & Parsing** — PDF/DOCX upload with LLM-powered structured extraction (skills, experience, projects, education) and ATS compatibility scoring
- **Skill Gap Analysis** — Compares your resume against a target role's requirements using a canonical skills taxonomy (63+ skills, 7 role presets)
- **Personalized Recommendations** — Project ideas and learning resources grounded in your specific skill gaps
- **User Profiles** — Auto-created on registration, tracks all activity (resumes uploaded, gaps analyzed, best ATS score, recent activity feed)
- **Activity Sync** — Every action (resume upload, skill gap analysis) is automatically synced to your profile
- **JWT Authentication** — Secure signup/login with bcrypt password hashing

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Database | SQLite (local dev) / PostgreSQL (production) |
| Frontend | Next.js 15, React 19, Tailwind CSS |
| Auth | JWT (python-jose), bcrypt |
| Resume Parsing | pdfplumber, python-docx, Ollama (LLM) |
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
| `GET` | `/api/v1/resumes/{id}` | Yes | Get parsed resume |
| `PATCH` | `/api/v1/resumes/{id}` | Yes | Update resume fields |
| `POST` | `/api/v1/skill-gap` | Yes | Compute skill gap for target role |
| `GET` | `/health` | No | Health check |

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page with feature overview |
| `/register` | Create account |
| `/login` | Login |
| `/upload` | Drag-and-drop resume upload with ATS scoring |
| `/skill-gap` | Side-by-side have/missing skills with recommendations |
| `/dashboard` | Overview with stats and resume table |
| `/profile` | Full profile view with activity feed and edit form |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route handlers
│   │   │   ├── auth.py       # Signup/login
│   │   │   ├── resume.py     # Resume upload/parse
│   │   │   ├── skill_gap.py  # Skill gap computation
│   │   │   ├── profile.py    # User profile CRUD
│   │   │   └── health.py     # Health check
│   │   ├── agents/           # Core AI logic
│   │   │   ├── resume_agent.py   # PDF/DOCX parsing + LLM structuring
│   │   │   └── skill_agent.py    # Skill normalization + gap analysis
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── skill.py      # Skills, UserSkill, SkillGapResult
│   │   │   ├── job.py        # Job, JobMatch
│   │   │   ├── application.py
│   │   │   └── profile.py    # UserProfile with activity tracking
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── utils/
│   │       ├── auth.py       # JWT + bcrypt
│   │       ├── dependencies.py   # Auth dependency
│   │       └── activity_sync.py  # Auto-sync activities to profile
│   ├── tests/                # 9 passing tests
│   ├── init_db.py            # Create all tables
│   ├── seed_skills.py        # Seed 63 canonical skills
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
│       │   ├── profile/page.tsx   # User profile
│       │   ├── login/page.tsx     # Login
│       │   └── register/page.tsx  # Register
│       └── lib/
│           ├── api.ts        # API client (all endpoints)
│           └── auth.ts       # Token management
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
```

## Database

Uses SQLite for local development (zero setup). Switch to PostgreSQL by updating `DATABASE_URL` in `backend/.env`:

```
DATABASE_URL=sqlite+aiosqlite:///./career_agent.db          # default (local)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db  # production
```

### Tables

| Table | Purpose |
|-------|---------|
| `users` | Auth credentials |
| `user_profiles` | Display info + activity counters + recent activity feed |
| `resumes` | Uploaded resumes with parsed JSON + ATS scores |
| `skills` | Canonical skills taxonomy (63 seeded) |
| `user_skills` | Skills extracted from user resumes |
| `skill_gap_results` | Computed gap analyses |
| `jobs` | Job postings (for Phase 2) |
| `job_matches` | Match scores per job (for Phase 2) |
| `applications` | Application drafts (for Phase 2) |

## Configuration

Environment variables in `backend/.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./career_agent.db
JWT_SECRET_KEY=change-me-in-production
LLM_PROVIDER=ollama           # ollama or hosted
LLM_MODEL=llama3.2            # model name
LLM_BASE_URL=http://localhost:11434
```

## Roadmap

### Phase 1 (Current) — MVP Linear Pipeline
- [x] Resume upload + parsing
- [x] Skill normalization + gap analysis
- [x] User profiles with activity sync
- [x] JWT authentication
- [x] Full frontend (upload, gap analysis, dashboard, profile)

### Phase 2 — Agentic System
- [ ] LangGraph orchestrator with multi-agent pipeline
- [ ] Job Researcher Agent (Adzuna/JSearch API integration)
- [ ] Application Agent (tailored resume + cover letter drafting)
- [ ] Human approval gate
- [ ] Application tracker (kanban view)
- [ ] Weekly progress reports (Celery)

### Phase 3 — Production
- [ ] Vector store (Chroma/Qdrant) for RAG
- [ ] PostgreSQL migration
- [ ] Docker Compose deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Rate limiting + monitoring

## License

MIT
