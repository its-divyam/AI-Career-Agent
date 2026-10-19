# Weekly Report — Week 1

**Project:** Skillgraph — An AI-Powered Career Assistant  
**Date Range:** 01 September 2026 – 07 September 2026  
**Author:** Divyam Garg and Khilika Garg 
**Institution:** JIMS Greater Noida  

---

## 1. Executive Summary

During Week 1, the foundational architecture of Skillgraph was established. The core objective was to build a secure, user-isolated backend with authentication, resume parsing, skill-gap analysis, and a responsive frontend. All user data is scoped to a single authenticated user, ensuring complete privacy and isolation. The system leverages FastAPI for the backend, Next.js for the frontend, and Ollama (llama3.2) for local LLM-powered resume extraction.

By the end of Week 1, the full user-facing pipeline was functional: signup → login → resume upload → skill-gap analysis → recommendations, all protected by JWT authentication with per-user data isolation.

---

## 2. Objectives for Week 1

| # | Objective | Status |
|---|-----------|--------|
| 1 | Implement JWT-based authentication (signup, login) | ✅ Complete |
| 2 | Enforce `user_id` foreign key on all database tables | ✅ Complete |
| 3 | Build a secure `get_current_user` dependency | ✅ Complete |
| 4 | Implement resume upload with LLM-powered parsing | ✅ Complete |
| 5 | Build skill-gap analysis against a canonical taxonomy | ✅ Complete |
| 6 | Create a responsive frontend (upload, dashboard, skill-gap) | ✅ Complete |
| 7 | Establish a passing test suite | ✅ Complete |

---

## 3. Technical Implementation

### 3.1 Backend Architecture

The backend is built on **FastAPI** with **SQLAlchemy 2.0** (async) and **Alembic** for schema migrations. The database uses **SQLite** via `aiosqlite` for local development, with `asyncpg` included for PostgreSQL readiness.

#### Database Schema

Eight tables were created, all enforcing `user_id` as a foreign key:

| Table | Purpose |
|-------|---------|
| `users` | Auth credentials (email + bcrypt-hashed password) |
| `resumes` | Uploaded resumes with parsed JSON + ATS scores |
| `skills` | Canonical skills taxonomy (63 seeded skills) |
| `user_skills` | Skills extracted from user resumes |
| `skill_gap_results` | Computed gap analyses per user |
| `jobs` | Job postings catalog |
| `job_matches` | Match scores per user per job |
| `applications` | Application drafts with lifecycle status |

Every query filters by `user_id`, ensuring complete data isolation.

#### Authentication

Authentication uses **JWT** (via `python-jose`) with **bcrypt** password hashing. The `get_current_user` dependency validates the `Authorization: Bearer <token>` header on every protected endpoint, extracting the `user_id` from the JWT payload and attaching it to the request context.

```python
# Dependency pattern used throughout
async def get_current_user(token: str = Depends(HTTPBearer()), session: AsyncSession = Depends(get_session)):
    payload = jwt.decode(token.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user = await session.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```

#### Resume Parsing

Resumes are uploaded as PDF or DOCX files and parsed using **pdfplumber** and **python-docx** for text extraction, followed by LLM-powered structured extraction via **Ollama** (model: `llama3.2`). The extracted data includes skills, experience, projects, and education, stored as JSON in the `resumes` table alongside an **ATS compatibility score**.

#### Skill Gap Analysis

A canonical skills taxonomy of **63+ normalized skills** (with alias resolution, e.g., "tf" → "TensorFlow") is seeded into the database. When a user uploads a resume and selects a target role, the system:

1. Extracts skills from the parsed resume
2. Looks up required skills for the target role
3. Computes set-difference to identify missing skills
4. Generates personalized project ideas and learning resources grounded in the specific gaps

#### Job Matching

Jobs are ingested from the catalog with deterministic skill-overlap scoring. The matching engine uses word-boundary-aware keyword extraction and overlap scoring to rank jobs against the user's skill profile.

### 3.2 Frontend Architecture

The frontend is built on **Next.js 15** with **React 19** and **Tailwind CSS v4**. The application uses a server-component architecture with selective client-side interactivity where needed.

#### Key Pages

- **Dashboard** — Overview with resume status, skill gaps, and job matching CTA
- **Upload** — Resume upload with parsing progress and ATS score display
- **Skill-Gap** — Interactive skill-gap analysis with target role selection
- **Login / Register** — JWT-based auth forms

#### Navigation

A shared `Nav.tsx` component (extracted as a server component) provides consistent navigation across all pages. All internal links use `next/link` for client-side routing, and the design follows a clean, accessible pattern.

### 3.3 Configuration and Environment

All configuration is managed via `pydantic-settings` with a `.env` file. Key settings include database URL, JWT secrets, LLM parameters, ChromaDB persistence directory, and file upload size limits.

### 3.4 Testing

A test suite was established using **pytest** and **pytest-asyncio**. Tests cover:

- ATS score computation (full vs. minimal resumes)
- Resume text extraction fallback
- Skill normalization (aliases like "tf" → "TensorFlow")
- Skill gap computation (partial and full skill sets)
- Role-based skill requirements
- Auth and user isolation

**Result: 9 passing tests.**

---

## 4. Challenges and Solutions

### Challenge 1: User Data Isolation
**Problem:** Ensuring that every query filters by `user_id` without forgetting it on any endpoint.  
**Solution:** A `get_current_user` dependency that injects `user_id` into every request, combined with a consistent pattern of filtering all queries. Verified by testing cross-user access attempts.

### Challenge 2: LLM Parsing Reliability
**Problem:** The LLM occasionally returned inconsistent JSON structures from resume parsing.  
**Solution:** Implemented a structured extraction prompt with explicit JSON schema instructions and a fallback parser for edge cases.

### Challenge 3: Development Environment Setup
**Problem:** Ensuring consistent behavior across Python venv, Next.js frontend, and Ollama.  
**Solution:** Documented `start.ps1` for backend startup and standard `next dev` for the frontend, with clear port assignments (8001 backend, 3000 frontend).

---

## 5. Verification Metrics

| Metric | Value |
|--------|-------|
| Backend tests passing | 9 / 9 |
| API endpoints exposed | 9 |
| Database tables | 8 |
| Frontend pages | 6 |
| Auth methods | JWT + bcrypt |
| Resume formats supported | PDF, DOCX |
| Seeded skills | 63 |
| LLM model | llama3.2 (Ollama) |

---

## 6. Summary and Look Ahead

Week 1 established the complete foundation: a secure, user-isolated backend with full authentication, resume parsing, skill-gap analysis, and a responsive frontend. The system is fully functional end-to-end.

**Week 2 focus:** Upgrade the system to an agentic architecture — integrating LangGraph for multi-step analysis orchestration, ChromaDB for retrieval-augmented recommendations, and Celery for background task processing.

---

*Report generated for academic review.*
