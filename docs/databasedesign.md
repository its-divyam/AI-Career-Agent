# Database Design

## 1. Storage split

- **PostgreSQL** — structured, relational data: users, resumes, jobs, applications, skill profiles, agent run logs.
- **Vector store (Chroma / Qdrant)** — embeddings for resumes, job descriptions, and knowledge-base chunks (projects, achievements) used for RAG retrieval.

Postgres is the source of truth; the vector store holds embeddings keyed back to Postgres record IDs so the two stay in sync.

## 2. Core tables (Prisma schema, conceptual)

### users
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| email | string | unique |
| created_at | timestamp | |

### resumes
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| raw_file_url | string | stored file location |
| parsed_json | jsonb | structured resume (skills, experience, projects) |
| ats_score | int | |
| version | int | resumes can be re-uploaded; keep history |
| created_at | timestamp | |

### skills
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| name | string | canonical name |
| aliases | string[] | e.g. "TF" → "TensorFlow" |
| category | string | e.g. language, framework, tool |

### user_skills
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| skill_id | uuid | FK → skills |
| source | string | "resume" / "manually added" |
| confidence | float | extraction confidence |

### target_roles
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| role_name | string | |
| required_skill_ids | uuid[] | seeded mapping, editable |

### jobs
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| source | string | e.g. "adzuna" |
| external_id | string | dedupe key from source |
| title | string | |
| company | string | |
| location | string | |
| raw_description | text | |
| structured_requirements | jsonb | LLM-extracted requirements |
| posted_at | timestamp | |

### job_matches
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| job_id | uuid | FK → jobs |
| match_score | float | |
| match_reasons | jsonb | retrieved evidence for the score |
| skill_gap | jsonb | per-job gap snapshot |
| created_at | timestamp | |

### applications
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| job_id | uuid | FK → jobs |
| resume_version | int | which resume version was used |
| draft_resume_json | jsonb | tailored/reordered version |
| draft_cover_letter | text | |
| status | enum | drafted / approved / applied / response_received / rejected |
| approved_at | timestamp | nullable |
| applied_at | timestamp | nullable |
| updated_at | timestamp | |

### agent_runs
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| agent_name | string | resume / job_researcher / skill / application |
| input_summary | jsonb | for debugging/audit, not full raw prompts |
| output_summary | jsonb | |
| status | string | success / error |
| created_at | timestamp | |

### progress_reports
| Field | Type | Notes |
|---|---|---|
| id | uuid | PK |
| user_id | uuid | FK → users |
| week_start | date | |
| summary_json | jsonb | applications sent, response rate, top gaps closing |
| created_at | timestamp | |

## 3. Vector store collections

- `resume_chunks` — chunks of parsed resume/project descriptions, keyed by `resume_id`
- `job_chunks` — chunks of structured job descriptions, keyed by `job_id`
- `kb_chunks` — broader career knowledge base entries (achievements, project write-ups) the user adds beyond the resume itself

Each vector record stores the Postgres foreign key as metadata so retrieval results can be joined back to structured data.

## 4. Entity relationships (conceptual ERD)

```
users ||--o{ resumes : uploads
users ||--o{ user_skills : has
users ||--o{ target_roles : sets
users ||--o{ job_matches : receives
users ||--o{ applications : drafts
users ||--o{ progress_reports : receives
jobs ||--o{ job_matches : matched_in
jobs ||--o{ applications : applied_to
skills ||--o{ user_skills : referenced_by
```

## 5. Indexing notes

- Index `user_skills(user_id)`, `job_matches(user_id, match_score)`, and `applications(user_id, status)` — these are the hot query paths for the dashboard and tracker views.
- `jobs(source, external_id)` should be a unique constraint to prevent duplicate ingestion from repeated API pulls.
