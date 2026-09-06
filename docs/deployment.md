# Deployment Strategy

## 1. Environments

- **Local dev:** Docker Compose running FastAPI, Next.js, Postgres, Redis, Chroma, and Ollama — fully self-contained, no external API costs while iterating.
- **Staging:** Same containers deployed to a low-cost cloud environment (e.g. a single VPS or a free-tier platform) with hosted Postgres and a hosted LLM API swapped in for realistic quality testing.
- **Production:** Scaled version of staging with managed services where it matters (managed Postgres, managed Redis) and monitoring in place.

## 2. Containerization

- Separate Dockerfiles for the FastAPI backend, the Next.js frontend, and Celery workers.
- `docker-compose.yml` for local dev wiring together: `api`, `web`, `worker`, `redis`, `postgres`, `chroma`, `ollama`.
- Keep the LLM provider swappable via environment variable (`LLM_PROVIDER=ollama|hosted`) so the same codebase runs cheaply in dev and at higher quality in production without code changes.

## 3. CI/CD

- GitHub Actions pipeline:
  1. Lint + type-check (backend: `ruff`/`mypy`; frontend: `eslint`/`tsc`)
  2. Run test suite from `testing.md` (unit + integration, mocked externals)
  3. Build Docker images
  4. Deploy to staging automatically on merge to `main`
  5. Manual promotion step to production
- Run the golden-set LLM evaluation as a separate, less frequent workflow (nightly or on prompt/model changes) since it costs real API calls and takes longer.

## 4. Infrastructure options (pick based on budget/scale)

| Component | Low-cost option | Scaled option |
|---|---|---|
| API hosting | Single VPS (Railway, Render, Fly.io) | Container orchestration (ECS/Kubernetes) |
| Postgres | Managed free/low tier (Supabase, Neon) | Managed Postgres with read replicas |
| Redis | Managed free tier (Upstash) | Managed Redis cluster |
| Vector store | Self-hosted Chroma on the same VPS | Managed Qdrant Cloud |
| LLM | Ollama on a GPU-enabled instance, or hosted API pay-per-use | Hosted API with provisioned throughput |
| Background jobs | Celery worker container alongside API | Autoscaled worker pool |

Start in the left column — this project doesn't need Kubernetes on day one, and over-engineering infra early slows down actually shipping the product.

## 5. Scheduled jobs

- Celery Beat schedules the weekly progress-report generation and periodic job-source polling/caching.
- Keep scheduled job failures alerting (even just a log-based alert in early stages) since a silently-failing weekly report defeats its purpose.

## 6. Monitoring & observability

- Application logs: structured JSON logs from FastAPI and Celery, shipped to a log aggregator (even a simple hosted option like Better Stack/Papertrail is enough at this scale).
- Track LLM call latency and cost per endpoint — this is your main operating cost and the thing most likely to surprise you as usage grows.
- Basic uptime monitoring on the API and frontend.
- Track the golden-set evaluation pass rate over time (see `testing.md`) as a quality-regression signal in production, not just in CI.

## 7. Rollout approach

- Ship Phase 1 (linear pipeline) to a small set of real users first — friends, classmates — before building the full agentic version. Real usage will surface resume-parsing edge cases and prompt issues faster than synthetic testing will.
- Feature-flag the agentic upgrade (Phase 2) so you can roll it out gradually and fall back to the simpler pipeline if something breaks.

## 8. Cost management

- Set hard per-user rate limits (see `security.md`) before any public rollout — an uncapped LLM-calling endpoint is the single most common way a side project generates an unexpectedly large bill.
- Default to the local/Ollama path for development and low-stakes extraction tasks; reserve hosted-API calls for generation-quality-sensitive steps (cover letters, final ranking).
