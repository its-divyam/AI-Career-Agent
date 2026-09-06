# Testing Strategy

Testing an agentic system means testing three different kinds of things: normal deterministic code, LLM-dependent behavior, and end-to-end user flows. Treat these differently — you cannot unit-test an LLM output for exact equality.

## 1. Unit tests (deterministic code)

- Resume file parsing (text extraction from PDF/DOCX) — test against a small set of sample resumes with known expected text.
- Skill normalization/taxonomy matching (e.g. "TF" → "TensorFlow") — pure function, fully testable.
- Skill-gap set-difference logic — pure function, fully testable.
- Database models and API request/response validation (Pydantic schemas) — standard FastAPI test client coverage.

Tooling: `pytest` for the backend, `pytest-asyncio` for async FastAPI routes.

## 2. LLM output evaluation (non-deterministic components)

Don't assert exact string equality on LLM outputs. Instead:
- Build a small **golden dataset**: 15-20 real resume/job-description pairs with human-reviewed expected structured outputs (skills list, requirements, match score range).
- Evaluate structured extraction by checking the *shape* is correct (valid JSON, required fields present, skills come from the canonical taxonomy) rather than exact text match.
- For match scoring, assert the score falls within an acceptable range and that the top-1 or top-3 ranking matches human judgment on the golden set, rather than an exact score.
- For generated text (cover letters), use a rubric-based check — either a second LLM call scoring the output against criteria (mentions the right company/role, references real user projects, no fabricated claims) or manual spot review during development.
- Track this golden-set pass rate over time — it's your regression signal when you change prompts or swap models.

## 3. Agent/orchestration tests (LangGraph)

- Test each graph node in isolation with mocked sub-agent calls — confirm the orchestrator routes correctly given different states (e.g. "no resume yet" routes to upload prompt, "resume + job selected" routes to Application Agent).
- Test state persistence/checkpointing — simulate a session interruption and confirm the graph resumes from the correct state.
- Test the human-approval gate explicitly: assert that no code path can reach an "applied" status without an "approved" status first. This is a correctness-critical test, not just a nice-to-have.

## 4. Integration tests

- Full pipeline test with mocked LLM and mocked job-source API: upload resume → search jobs → generate application → approve → mark applied, asserting each stage's data lands correctly in Postgres and the vector store.
- Test failure/degradation paths: job-source API returns an error → system should degrade gracefully (cached results or a clear error), not crash the whole request.

## 5. API contract tests

- Use FastAPI's test client to verify every endpoint in `apispecification.md` against expected status codes, response shapes, and auth enforcement (an unauthenticated or cross-user request must be rejected).

## 6. Frontend testing

- Component tests (React Testing Library) for the approval screen specifically — verify the "approve" action is genuinely blocked until required fields are present, and that no auto-submit path exists.
- End-to-end tests (Playwright) for the core user journey: upload → gap report → job matches → draft application → approve → tracker update.

## 7. Load/performance testing

- Load-test the job-search and application-drafting endpoints (the LLM-heavy ones) since these are your bottleneck and cost center — use `locust` or similar to simulate concurrent users and confirm rate limiting and queuing (Celery) behave as expected under load.

## 8. CI pipeline

- Run unit + integration tests (with mocked LLM/API calls) on every PR.
- Run the golden-set LLM evaluation on a schedule (e.g. nightly or on prompt changes) rather than every commit, since it's slower and costs real API calls.
- Run dependency vulnerability scans as part of CI (see `security.md`).
