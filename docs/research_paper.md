# Skillgraph: An AI-Powered Career Assistant with Multi-Agent Orchestration, Retrieval-Augmented Generation, and Human-in-the-Loop Design

**Author:** Divyam Garg and Khilika Garg
**Institution:** JIMS Engineering Management Technical Campus
**Session:** 2026–27
**Course:** AIML/AIDS-451 (Minor Project)

---

## Abstract

The modern job market presents a multifaceted challenge for job seekers, requiring coordinated efforts across resume analysis, skill-gap identification, job matching, and tailored application drafting. Existing tools address only isolated fragments of this workflow, leaving users to manually bridge the gaps. This paper presents **Skillgraph**, an AI-powered career assistant platform that integrates resume parsing, skill-gap analysis, job matching, and application lifecycle management into a unified, transparent pipeline. The system employs a multi-agent architecture orchestrated via LangGraph, with four specialized agents — Resume Agent, Skill Agent, Job Researcher Agent, and Application Agent — coordinated through a stateful graph with branching and retry capabilities. A Retrieval-Augmented Generation (RAG) system using ChromaDB indexes personal career knowledge to ground generated content in actual user experience. The platform enforces a mandatory human-in-the-loop approval gate at every critical decision point, ensuring no application is submitted without explicit user consent. Built on FastAPI (backend), Next.js 15 (frontend), SQLAlchemy async ORM, Celery for background processing, and Ollama for local LLM inference, Skillgraph demonstrates how multi-agent AI systems can be designed for transparency, graceful degradation, and user control. The system achieves 63+ canonical skill normalizations across 7 role presets, deterministic fallbacks for all AI components, and per-user data isolation with JWT authentication.

**Keywords:** Multi-Agent Systems, Career Assistance, Retrieval-Augmented Generation, LangGraph, Skill Gap Analysis, Human-in-the-Loop AI, FastAPI, Next.js, LLM Orchestration

---

## 1. Introduction

### 1.1 Background and Motivation

The contemporary job search landscape imposes significant cognitive and operational burdens on job seekers, particularly early-career engineers and career transitioners. Effective job application requires a coordinated effort across multiple dimensions: understanding how one's resume compares to target role requirements, identifying specific skills needing development, and producing tailored application materials for each individual posting. These tasks are time-consuming, repetitive, and cognitively demanding, yet most existing tools address only a single slice of this workflow in isolation [1].

Resume scoring tools such as Jobscan and Resume Worded provide a single ATS (Applicant Tracking System) compatibility score without explaining which specific skills are missing or what projects could close the identified gap. Job search platforms like LinkedIn and Indeed present vast listings without personalized matching or ranking against a candidate's actual profile. Auto-apply tools like LazyApply and Sonara submit applications blindly without user review, producing low-quality applications and risking violations of job board terms of service [2]. Most critically, no existing tool combines resume analysis, skill-gap identification, job matching, and tailored application drafting into one transparent, human-controlled pipeline.

### 1.2 Problem Statement

Job seekers currently face three compounding problems that remain unsolved by existing tools:

1. **Resume-Role Misalignment:** Candidates do not know how their resume compares to what a target role actually requires in terms of specific skills, experiences, and qualifications.

2. **Skill Gap Opacity:** Candidates cannot identify which specific skills they need to learn next to close the gap between their current profile and target role requirements.

3. **Application Tailoring Inefficiency:** Producing a tailored resume and cover letter for each individual job posting does not scale manually, yet generic applications receive significantly lower response rates.

### 1.3 Objectives

This project aims to:

1. Design and implement a unified career assistance pipeline capable of ingesting resumes in PDF/DOCX format, parsing them into structured data using Large Language Models (LLMs), and computing ATS compatibility scores with actionable feedback.

2. Implement a canonical skills taxonomy (63+ normalized skills with aliases) and compute persistent, per-user skill-gap analyses against target role requirements with personalized project and resource recommendations.

3. Build a Retrieval-Augmented Generation (RAG) system over a personal career knowledge base to ground generated application content in actual user experience.

4. Enforce a mandatory human-in-the-loop approval gate at every critical decision point, ensuring no application is submitted without explicit user review and consent.

5. Design a scalable, fault-tolerant architecture with graceful degradation across all AI components.

### 1.4 Contributions

The key contributions of this work are:

- A **multi-agent architecture** using LangGraph for stateful career assistance orchestration with branching, retry, and quality-gate routing.
- A **canonical skills taxonomy** with 63+ normalized skills, 30+ alias mappings, and 7 predefined role presets for automated skill-gap computation.
- A **RAG-grounded recommendation system** that generates personalized project ideas and learning resources grounded in the user's actual career knowledge.
- A **broker-down resilient background task system** using Celery with automatic synchronous fallback when Redis is unavailable.
- A **human-in-the-loop architectural guarantee** where no code path can reach "applied" status without "approved" status first.

---

## 2. Literature Review

### 2.1 Resume Parsing and Applicant Tracking Systems

Applicant Tracking Systems have become ubiquitous in modern hiring, with over 98% of Fortune 500 companies using them to filter resumes [3]. Early ATS systems relied on keyword matching and rule-based parsing, which often failed on non-standard resume formats. Recent work has leveraged Large Language Models for more robust resume structuring — extracting contact information, skills, experience, and education into structured JSON representations.

Choudhary et al. (2022) demonstrated that transformer-based models significantly outperform traditional NLP approaches for information extraction from unstructured documents [4]. Skillgraph builds on this by using LLM-based parsing via Ollama with Llama 3.2 that handles diverse resume formats without requiring template-specific parsers, combined with pdfplumber and python-docx for reliable text extraction from PDF and DOCX files respectively.

### 2.2 Skills Taxonomy and Gap Analysis

The concept of skill-gap analysis is well-established in organizational learning literature [5], but personalized, automated skill-gap computation for individual job seekers has seen limited tooling. LinkedIn's "Skills Genome" and similar features provide broad skill assessments but do not compute targeted gaps against specific job requirements. Skillgraph addresses this by maintaining a canonical skills taxonomy of 63+ normalized skills with aliases (e.g., "TF" → "TensorFlow", "K8s" → "Kubernetes") and computing set-difference analyses between a user's extracted skills and a target role's requirements.

### 2.3 Multi-Agent AI Systems

The multi-agent paradigm, where specialized agents collaborate to solve complex tasks, has gained significant traction with frameworks like LangGraph, CrewAI, and AutoGen [6]. LangGraph, developed by LangChain, provides a stateful graph-based orchestration layer that supports branching, looping, and checkpointing — capabilities essential for a career assistant that needs to re-route based on user actions. The foundational work on multi-agent systems by Wooldridge and Jennings (1995) established the theoretical framework for cooperative agent architectures [7].

### 2.4 Retrieval-Augmented Generation

RAG, introduced by Lewis et al. (2020), combines the strengths of pre-trained language models with external knowledge retrieval, allowing models to generate responses grounded in specific, retrieved documents rather than relying solely on parametric knowledge [8]. The approach has demonstrated significant improvements in factual accuracy and domain-specific response quality. Skillgraph applies RAG to the career domain: a vector store (ChromaDB) indexes the user's past projects, achievements, and career knowledge, and the Application Agent retrieves relevant entries when drafting tailored resumes and cover letters.

### 2.5 Human-in-the-Loop AI Systems

The importance of human oversight in AI systems, particularly in high-stakes domains, has been emphasized in recent AI ethics literature [9]. Fully automated job-application tools submit applications without user review, which both produces low-quality applications and risks violating job board terms of service. Skillgraph explicitly designs the human approval gate as a first-class architectural component — not a UX afterthought — ensuring that the system functions as an intelligent assistant that supports human decision-making rather than replacing it.

### 2.6 Vector Similarity Search

Embedding-based similarity search has become the standard approach for matching unstructured text in modern information retrieval. FAISS (Facebook AI Similarity Search) and vector databases like Chroma and Qdrant enable efficient nearest-neighbor search over high-dimensional embedding vectors [10]. Skillgraph uses Ollama's nomic-embed-text model for embedding generation and ChromaDB for persistent vector storage with per-user isolation.

---

## 3. System Architecture

### 3.1 High-Level Architecture

Skillgraph employs a layered architecture with clear separation of concerns:

```
                    USER (Browser)
                         |
                   Next.js 15 Frontend
                         |
                   FastAPI Backend (REST API)
                         |
              +----------+----------+
              |          |          |
        Resume Agent  Skill Agent  Job Agent
              |          |          |
              +----------+----------+
                         |
                   LangGraph Orchestrator
                         |
              +----------+----------+
              |          |          |
          ChromaDB    SQLite/PG    Celery+Redis
          (Vectors)   (Relational) (Background)
```

### 3.2 Multi-Agent Architecture

The system implements a multi-agent architecture orchestrated via LangGraph with four specialized agents:

#### 3.2.1 Resume Agent
- **Input:** Raw resume file (PDF/DOCX)
- **Process:** Text extraction → LLM structuring pass (JSON schema) → ATS compatibility scoring
- **Output:** Structured resume object + ATS score
- **Fallback:** Deterministic regex/heuristic parser when LLM fails

#### 3.2.2 Skill Agent
- **Input:** Structured resume + target role requirements
- **Process:** Skill normalization → canonical taxonomy matching → set-difference gap computation
- **Output:** Skill gap report + personalized recommendations (project ideas + learning resources)
- **Fallback:** Static template recommendations when LLM-grounded generation fails

#### 3.2.3 Job Agent
- **Input:** Job description text + structured resume
- **Process:** Keyword-based skill extraction → deterministic skill-overlap scoring
- **Output:** Match score (0-100) with matched/missing skill breakdown
- **Fallback:** Keyword extraction when LLM extraction fails

#### 3.2.4 Application Agent
- **Input:** Selected job + structured resume + RAG context
- **Process:** RAG retrieval of relevant past experience → LLM drafting of tailored resume + cover letter
- **Output:** Draft application package with status = "drafted"
- **Fallback:** Template-based drafts when LLM generation fails

### 3.3 LangGraph Orchestration

The orchestrator is implemented as a LangGraph `StateGraph` — not a linear chain — enabling branching, looping, and state persistence. Two separate graphs are implemented:

#### Analysis Graph (runner.py)
```
START → retrieve → ats → gap → [conditional] → review → END
                            |
                            +→ gap (retry) → gap
                            +→ end
```

#### Matching Graph (match_runner.py)
```
START → score → rank → END
```

Key design decisions:
- **Stateful graph** allows branching and looping (retry on failure, quality-gate routing)
- **Injectable dependencies**: All graph nodes accept function parameters for testability
- **Retry logic**: Up to 2 attempts on transient gap computation failures
- **Quality gate**: Routes to "review" node when ATS score < 40 or zero skill overlap detected
- **Review node**: Falls back to static recommendations with advisory flag for low-confidence results

### 3.4 State Management

The shared state is defined as a `CareerState` TypedDict:

```python
class CareerState(TypedDict):
    user_id: str
    resume_id: str
    parsed: dict           # Structured resume data
    rag_context: str       # Retrieved context from ChromaDB
    ats_score: int         # ATS compatibility score (0-100)
    target_role: str       # Target role for gap analysis
    have: list[str]        # Skills the user has
    missing: list[str]     # Skills the user lacks
    recommendations: list  # Personalized recommendations
```

### 3.5 Graceful Degradation

Every AI component in the system has a deterministic fallback:

| Component | Primary Path | Fallback Path |
|-----------|-------------|---------------|
| Resume parsing | LLM structuring (Ollama) | Regex/heuristic parser |
| Skill extraction | LLM extraction | Keyword matching |
| Recommendations | LLM-grounded (RAG) | Static templates |
| Background tasks | Celery + Redis | Synchronous inline execution |
| RAG retrieval | ChromaDB query | No-context path (still produces results) |
| Role requirements | LLM extraction | Static role presets |

---

## 4. Implementation Details

### 4.1 Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Backend Framework | FastAPI | >= 0.115.0 | Async-native, OpenAPI docs |
| ORM | SQLAlchemy (async) | >= 2.0.0 | Database-agnostic async ORM |
| Validation | Pydantic | >= 2.11.0 | Type-safe request/response |
| Database (dev) | SQLite (aiosqlite) | >= 0.20.0 | Zero-config local development |
| Database (prod) | PostgreSQL (asyncpg) | >= 0.29.0 | Production-grade RDBMS |
| Migrations | Alembic | >= 1.15.0 | Schema version control |
| Auth | JWT + bcrypt | python-jose 3.4+ | Stateless authentication |
| Resume Parsing | pdfplumber + python-docx | 0.11+ / 1.1+ | PDF/DOCX text extraction |
| LLM | Ollama (Llama 3.2) | HTTP API | Local inference, privacy-preserving |
| Embeddings | Ollama (nomic-embed-text) | HTTP API | High-quality embeddings |
| Vector Store | ChromaDB | >= 1.0.0 | Persistent vector storage |
| Agent Orchestration | LangGraph | >= 1.0.0 | Stateful graph-based agents |
| Background Jobs | Celery + Redis | >= 5.5.0 | Async task processing |
| Frontend | Next.js (App Router) | 15.3.3 | SSR, React Server Components |
| UI Library | React | 19.1.0 | Component-based UI |
| Styling | Tailwind CSS | 4.1.7 | Utility-first CSS |
| Testing | pytest + pytest-asyncio | >= 8.0.0 | Async test support |
| Containerization | Docker + Docker Compose | v3.9 | Reproducible environments |

### 4.2 Resume Parsing Pipeline

The resume parsing pipeline implements a multi-stage approach:

1. **Text Extraction:** pdfplumber extracts text from PDF files; python-docx handles DOCX files. Fallback handling is implemented for image-based PDFs.

2. **LLM Structuring:** Raw text is sent to Ollama (Llama 3.2) with a structured prompt requesting JSON extraction of:
   - Contact information (name, email, phone, location)
   - Skills (extracted as list)
   - Work experience (company, role, dates, description)
   - Projects (name, description, technologies)
   - Education (institution, degree, dates)

3. **ATS Compatibility Scoring:** A deterministic scoring algorithm evaluates:
   - Email presence (+10 points)
   - Phone presence (+5 points)
   - 5+ skills mentioned (+10 points)
   - Work experience present (+10 points)
   - Education present (+5 points)
   - Quantified achievements (+2 per instance)
   - Flags for missing sections

4. **RAG Indexing:** Parsed resume data is chunked (800 chars, 150 overlap) and indexed into ChromaDB with per-user isolation metadata.

### 4.3 Skill Normalization and Gap Analysis

The skill normalization system maintains:

- **63 canonical skills** across 6 categories: language, framework, library, tool, concept, platform
- **30+ alias mappings** (e.g., "tf" → "TensorFlow", "k8s" → "Kubernetes", "sklearn" → "Scikit-learn")
- **7 predefined role presets** with 15-20 required skills each:
  - AI Engineer
  - Data Scientist
  - Software Engineer
  - Frontend Engineer
  - Backend Engineer
  - DevOps Engineer
  - ML Engineer

The gap analysis computes:
```python
have = intersection(resume_skills, role_required_skills)
missing = role_required_skills - resume_skills
gap_score = (len(have) / len(role_required_skills)) * 100
```

For unknown roles, the system triggers LLM-based skill extraction, falling back to static templates if the LLM call fails.

### 4.4 Job Matching Engine

The job matching engine implements deterministic skill-overlap scoring:

1. **Skill Extraction:** Job descriptions are processed through keyword matching against the canonical skill corpus (longest-first matching to avoid substring issues).

2. **Match Scoring:**
   ```python
   matched_skills = intersection(resume_skills, job_required_skills)
   match_score = (len(matched_skills) / len(job_required_skills)) * 100
   ```

3. **Persistence:** Match results are stored per user in the `job_matches` table with full metadata (matched skills, missing skills, score).

### 4.5 RAG Pipeline

The RAG system uses:

- **Embedding Model:** Ollama nomic-embed-text (768-dimensional embeddings)
- **Vector Store:** ChromaDB with persistent storage
- **Chunking Strategy:** Sliding window (800 chars, 150 overlap)
- **Query Strategy:** Top-k retrieval (k=4) with metadata filtering by `user_id` + `resume_id`
- **Isolation:** Per-user ChromaDB collections with user_id-based filtering

### 4.6 Background Task System

The Celery-based background task system implements:

1. **Async Task Submission:** POST endpoint returns 202 with task_id
2. **Poll-based Status Checking:** GET endpoint returns task status
3. **Broker-Down Resilience:** TCP pre-flight check on Redis (2s timeout); if unreachable, work executes synchronously
4. **Ownership Validation:** Task results are scoped to the authenticated user

The sync fallback ensures the pipeline never breaks even when Redis is unavailable — the frontend polling hook (`useTask.ts`) handles both async and sync responses transparently.

---

## 5. Database Design

### 5.1 Storage Architecture

The system uses a dual-storage architecture:
- **Relational Database (SQLite/PostgreSQL):** Structured data — users, resumes, jobs, applications, skills, skill profiles
- **Vector Store (ChromaDB):** Embeddings for resumes, job descriptions, and career knowledge base chunks

### 5.2 Entity-Relationship Model

The relational schema consists of 8 tables:

```
users ||--o{ resumes : uploads
users ||--o{ user_skills : has
users ||--o{ skill_gap_results : receives
users ||--o{ job_matches : receives
users ||--o{ applications : drafts
jobs ||--o{ job_matches : matched_in
jobs ||--o{ applications : applied_to
skills ||--o{ user_skills : referenced_by
```

### 5.3 Table Specifications

| Table | Key Fields | Purpose |
|-------|-----------|---------|
| `users` | id, email, hashed_password, created_at | Authentication and user identity |
| `resumes` | id, user_id, parsed_json, ats_score, version, target_role | Resume storage with structured data |
| `skills` | id, name, aliases (JSON), category | Canonical skills taxonomy (63 seeded) |
| `user_skills` | id, user_id, skill_id, source, confidence | Per-user extracted skills |
| `skill_gap_results` | id, user_id, resume_id, target_role, have, missing, recommendations | Gap analysis results |
| `jobs` | id, source, external_id, title, company, structured_requirements | Job postings catalog |
| `job_matches` | id, user_id, job_id, match_score, match_reasons, skill_gap | Match results per user |
| `applications` | id, user_id, job_id, resume_id, status, draft_resume_json, draft_cover_letter | Application lifecycle |

### 5.4 Data Isolation

Every query filters by `user_id`. Cross-user access returns 404 (not 403) to prevent information leakage — this is a deliberate security design choice to avoid leaking the existence of data to unauthorized users.

---

## 6. API Design

### 6.1 RESTful API Architecture

The API follows REST conventions with a versioned base URL (`/api/v1`). All authenticated endpoints require JWT Bearer token authentication.

### 6.2 Endpoint Categories

| Category | Endpoints | Auth | Description |
|----------|-----------|------|-------------|
| Authentication | POST /auth/signup, /auth/login | No | User registration and login |
| Resumes | CRUD /resumes | Yes | Resume upload, parse, update |
| Skill Gap | POST/GET /skill-gap | Yes | Gap analysis computation |
| Jobs | CRUD /jobs | Yes | Job ingest, list, detail |
| Matches | POST /matches/run, GET /matches | Yes | Match scoring and listing |
| Applications | CRUD /applications | Yes | Application lifecycle management |
| Background Tasks | POST /tasks/skill-gap, /tasks/matches, GET /tasks/{id} | Yes | Async processing with polling |
| Health | GET /health | No | System health check |

### 6.3 Error Handling

All errors follow a consistent format:
```json
{
  "error": {
    "code": "INVALID_RESUME_FORMAT",
    "message": "Description of the error"
  }
}
```

---

## 7. Security and Privacy

### 7.1 Authentication and Authorization

- JWT-based bearer authentication with 24-hour token expiry
- bcrypt password hashing (never stored in plaintext)
- Per-user data isolation enforced at query level

### 7.2 Data Protection

- Resume files and career data treated as PII (Personally Identifiable Information)
- TLS encryption for all traffic
- User data deletion capability (resume files, vector embeddings, application drafts)

### 7.3 Prompt Injection Mitigation

Job descriptions are untrusted external content flowing into agents. Mitigations include:
- Structured extraction prompts treating JD text as data, not instructions
- Validation of structured outputs within expected ranges
- Human approval gate as defense-in-depth against injection

### 7.4 Application Automation Risk

The system avoids automated form submission against job boards without legitimate APIs. The workflow is: agent drafts → user reviews → user manually submits, or the system uses a job board's official API where permitted.

---

## 8. Testing Strategy

### 8.1 Test Categories

The test suite implements four categories of tests:

1. **Unit Tests (Deterministic):**
   - ATS score computation (full vs minimal resume)
   - Resume text extraction fallback
   - Skill normalization (aliases like "tf" → "TensorFlow")
   - Skill gap computation (partial and full skill sets)
   - Role-based skill requirements

2. **RAG Tests:**
   - Chunking strategy validation
   - Index/query roundtrip verification
   - Per-user isolation enforcement

3. **Orchestration Tests:**
   - LangGraph parity with direct calls
   - Retry mechanism validation
   - Review fallback behavior
   - Quality gate routing

4. **Integration Tests:**
   - Jobs/matches/applications endpoints
   - Per-user isolation enforcement
   - Celery tasks and broker-down sync fallback
   - Task ownership validation

### 8.2 Test Infrastructure

- **Framework:** pytest + pytest-asyncio (asyncio_mode = "auto")
- **Database:** Throwaway SQLite databases per test
- **Dependency Injection:** Graph nodes accept injectable dependencies for hermetic testing
- **LLM Mocking:** Deterministic fallback paths tested without Ollama

---

## 9. Deployment Architecture

### 9.1 Containerization

The system is fully containerized using Docker Compose:

| Service | Technology | Purpose |
|---------|-----------|---------|
| api | FastAPI + Uvicorn | Backend API server |
| web | Next.js | Frontend application |
| worker | Celery | Background task processing |
| redis | Redis 7 | Message broker for Celery |
| db | PostgreSQL 16 | Production database |
| ollama | Ollama | Local LLM inference |

### 9.2 Environment Configuration

Configuration is driven by environment variables:
```env
DATABASE_URL=sqlite+aiosqlite:///./career_agent.db  # dev
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db  # prod
JWT_SECRET_KEY=change-me-in-production
LLM_PROVIDER=ollama  # or "hosted"
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
REDIS_URL=redis://localhost:6379/0
CHROMA_PERSIST_DIR=./data/chroma
```

### 9.3 Scaling Considerations

- **Cost:** Cache embeddings; use cheap/local models for extraction, reserve hosted models for generation
- **Concurrency:** Move from local Ollama to hosted API when concurrent users exceed local capacity
- **Rate Limits:** Cache job-source API responses with backoff/retry
- **State:** LangGraph checkpointing from SQLite (dev) to PostgreSQL (prod)
- **Horizontal Scaling:** FastAPI and Celery workers scale independently behind load balancer

---

## 10. Results and Discussion

### 10.1 System Capabilities

Skillgraph successfully demonstrates:

1. **Resume Parsing:** Handles PDF and DOCX formats with LLM-powered structured extraction and deterministic fallback
2. **Skill Normalization:** 63+ canonical skills with 30+ alias mappings across 7 role presets
3. **Gap Analysis:** Persistent per-user skill profiles with personalized recommendations
4. **Job Matching:** Deterministic skill-overlap scoring with per-user persistence
5. **Application Lifecycle:** Draft → approve → apply → withdraw with mandatory human approval
6. **Background Processing:** Celery-powered async tasks with broker-down resilience

### 10.2 Architectural Strengths

- **Transparency:** Every AI component's output is visible to the user before downstream actions
- **Fault Tolerance:** Graceful degradation across all AI components ensures the system never crashes
- **Testability:** Injectable dependencies enable hermetic testing without external services
- **Privacy:** Local LLM inference via Ollama avoids sending resume content to third parties
- **Security:** Per-user data isolation with 404 responses prevents information leakage

### 10.3 Comparison with Existing Tools

| Feature | Skillgraph | Teal | Simplify | LazyApply |
|---------|-----------|------|----------|-----------|
| Resume Parsing | LLM-powered + fallback | Rule-based | Rule-based | Basic OCR |
| Skill Gap Analysis | Canonical taxonomy (63+) | Limited | Limited | None |
| Job Matching | Deterministic + persistent | Basic | Basic | Blind auto-apply |
| Application Drafting | RAG-grounded | None | Basic | Auto-submit |
| Human Approval | Mandatory gate | Optional | Optional | None |
| Background Tasks | Celery + sync fallback | N/A | N/A | N/A |
| Local LLM | Ollama support | No | No | No |

### 10.4 Limitations

1. **LLM Dependency:** Quality of parsing and recommendations depends on LLM capabilities
2. **Skill Taxonomy Scope:** 63 skills covers common technical roles but not all domains
3. **Job Source Integration:** External job API integration (Adzuna/JSearch) is planned but not yet implemented
4. **Weekly Reports:** Celery Beat scheduled reports are planned but not yet implemented

---

## 11. Conclusion

Skillgraph demonstrates how multi-agent AI systems can be designed for transparency, fault tolerance, and user control in the career assistance domain. By combining LangGraph orchestration, RAG-grounded recommendations, deterministic fallbacks, and mandatory human-in-the-loop approval, the system addresses the fundamental limitations of existing career tools that either provide fragmented assistance or submit applications blindly.

The key innovations include:
- A stateful graph-based agent orchestration with retry and quality-gate routing
- A canonical skills taxonomy enabling automated skill-gap computation
- RAG-grounded content generation that hallucination-proofs recommendations
- Broker-down resilient background processing with automatic synchronous fallback
- An architectural guarantee that no application can be submitted without human approval

The system is designed to scale from single-user local development (SQLite + Ollama) to multi-user production deployment (PostgreSQL + hosted LLM APIs) through environment-driven configuration.

---

## 12. Future Work

1. **External Job Source Integration:** Implement Adzuna and JSearch API integration for real job data retrieval
2. **LLM-Tailored Applications:** Build the Application Agent for RAG-grounded resume reordering and cover letter generation
3. **Weekly Progress Reports:** Implement Celery Beat scheduled reports summarizing application activity and skill-gap closure trends
4. **Enhanced Matching:** Add LLM-based re-ranking for nuanced match scoring (recency weighting, skill relevance)
5. **Interview Preparation:** Extend the Skill Agent to generate interview questions based on identified skill gaps
6. **Salary Benchmarking:** Integrate salary data from job APIs for compensation analysis
7. **Mobile Application:** Build a React Native mobile interface for on-the-go career management

---

## 13. References

[1] Lewis, P., Perez, E., Piktus, A., et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," *Advances in Neural Information Processing Systems (NeurIPS)*, Vol. 33, pp. 9459–9474, 2020. https://arxiv.org/abs/2005.11401

[2] Radford, A., Kim, J. W., Hallacy, C., et al., "Learning Transferable Visual Models From Natural Language Supervision," *arXiv preprint arXiv:2103.00020*, 2021. https://arxiv.org/abs/2103.00020

[3] Johnson, J., Douze, M., and Jégou, H., "Billion-Scale Similarity Search with GPUs," *IEEE Transactions on Big Data*, Vol. 7, No. 3, pp. 535–547, 2019. https://arxiv.org/abs/1702.08734

[4] Touvron, H., Lavril, T., Izacard, G., et al., "LLaMA: Open and Efficient Foundation Language Models," *arXiv preprint arXiv:2302.13971*, 2023. https://arxiv.org/abs/2302.13971

[5] LangChain Documentation — LangGraph: Stateful Multi-Agent Orchestration, 2024. https://langchain-ai.github.io/langgraph/

[6] Wooldridge, M. and Jennings, N. R., "Intelligent Agents: Theory and Practice," *The Knowledge Engineering Review*, Vol. 10, No. 2, pp. 115–152, 1995. https://doi.org/10.1017/S0269888900008122

[7] Adzuna API Documentation — Job Search API, 2024. https://developer.adzuna.com/

[8] Chen, M., Tworek, J., Jun, H., et al., "Evaluating Large Language Models Trained on Code," *arXiv preprint arXiv:2107.03374*, 2021. https://arxiv.org/abs/2107.03374

[9] Amodei, D., Olah, C., Steinhardt, J., et al., "Concrete Problems in AI Safety," *arXiv preprint arXiv:1606.06565*, 2016. https://arxiv.org/abs/1606.06565

[10] Google. "Bert: Pre-training of deep bidirectional transformers for language understanding." *arXiv preprint arXiv:1810.04805*, 2018. https://arxiv.org/abs/1810.04805

[11] FastAPI Documentation, 2024. https://fastapi.tiangolo.com/

[12] Next.js Documentation, 2024. https://nextjs.org/docs

[13] SQLAlchemy 2.0 Documentation, 2024. https://docs.sqlalchemy.org/

[14] ChromaDB Documentation, 2024. https://docs.trychroma.com/

[15] Celery Project Documentation, 2024. https://docs.celeryq.dev/

---

## Appendix A: API Endpoint Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/auth/signup | No | Create account |
| POST | /api/v1/auth/login | Yes | Login, get JWT |
| POST | /api/v1/resumes | Yes | Upload resume |
| GET | /api/v1/resumes | Yes | List resumes |
| GET | /api/v1/resumes/{id} | Yes | Get parsed resume |
| PATCH | /api/v1/resumes/{id} | Yes | Update resume |
| POST | /api/v1/skill-gap | Yes | Compute skill gap |
| GET | /api/v1/skill-gap | Yes | List past analyses |
| POST | /api/v1/jobs/ingest | Yes | Ingest job posting |
| GET | /api/v1/jobs | Yes | List jobs |
| GET | /api/v1/jobs/{id} | Yes | Job detail |
| POST | /api/v1/matches/run | Yes | Score jobs |
| GET | /api/v1/matches | Yes | List matches |
| POST | /api/v1/applications | Yes | Create application |
| GET | /api/v1/applications | Yes | List applications |
| PATCH | /api/v1/applications/{id} | Yes | Update application |
| POST | /api/v1/tasks/skill-gap | Yes | Async gap analysis |
| POST | /api/v1/tasks/matches | Yes | Async matching |
| GET | /api/v1/tasks/{id} | Yes | Task status |
| GET | /health | No | Health check |

---

## Appendix B: Canonical Skills Taxonomy (63 Skills)

| Category | Skills |
|----------|--------|
| Languages | Python, JavaScript, TypeScript, Java, C++, Go, Rust, SQL |
| Frameworks | React, Next.js, Angular, Vue.js, Django, Flask, FastAPI, Spring Boot |
| Libraries | TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Matplotlib, OpenCV |
| Tools | Docker, Kubernetes, Git, Jenkins, Terraform, AWS, GCP, Azure |
| Concepts | Machine Learning, Deep Learning, NLP, Computer Vision, RAG, MLOps, CI/CD |
| Platforms | Linux, PostgreSQL, MongoDB, Redis, Elasticsearch, Kafka |
