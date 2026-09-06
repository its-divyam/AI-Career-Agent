# AI Career Agent — Project Overview

## 1. Problem statement

Job seekers, especially early-career engineers, face three compounding problems:

1. They don't know how their resume compares to what a target role actually requires.
2. They don't know which specific skills to learn next to close that gap.
3. Applying to jobs well (tailored resume + cover letter per posting) doesn't scale manually.

Most existing tools solve one slice of this (resume scoring *or* job search *or* auto-apply) in isolation, and the auto-apply tools tend to submit blindly, which both produces low-quality applications and risks violating job board terms of service.

## 2. Vision

A career assistant that behaves like a competent human career coach: it reads your resume, understands your target role, tells you exactly what's missing, finds real jobs that fit, drafts tailored applications for you to review, and reports back on your progress over time — with a human always approving before anything is sent.

## 3. Goals

- Give the user an honest, specific skill-gap analysis instead of generic "resume feedback."
- Turn job search into a ranked, explained shortlist instead of endless manual scrolling.
- Reduce the time to produce a tailored application from ~30 minutes to a few minutes of review.
- Maintain a running "career knowledge base" so recommendations improve as the user adds projects/skills.
- Never submit an application without explicit human approval.

## 4. Non-goals (explicitly out of scope for v1)

- Fully autonomous auto-apply with no human in the loop.
- Interview scheduling or salary negotiation.
- Supporting every job board on day one — start with 1–2 API-based sources.
- Building a custom resume-parsing model from scratch (use LLM-based structuring instead).

## 5. Target users

- **Primary:** Students and early-career engineers (like the intended first user) applying to technical roles and needing to identify and close skill gaps.
- **Secondary:** Career switchers who need a structured gap analysis against a new target role.

## 6. Feature set by phase

### Phase 1 — MVP (linear pipeline)
- Resume upload (PDF/DOCX) → structured parsing
- Target role input
- Skill extraction and normalization against a canonical taxonomy
- Skill-gap report (have vs. need)
- Project/resource recommendations grounded in the gap

### Phase 2 — Agentic system
- Career Agent orchestrator (LangGraph state machine)
- Resume Agent (parsing + ATS scoring)
- Job Researcher Agent (job search + JD structuring + match ranking)
- Skill Agent (persistent, per-job skill-gap tracking)
- Application Agent (tailored resume reordering + cover letter drafts, RAG-grounded)
- Human Approval gate before any send/apply action
- Application tracker (status: drafted → approved → applied → response)
- Weekly progress report (auto-generated summary of activity and skill growth)

## 7. Success metrics

- % of resumes successfully parsed without manual correction
- Average skill-gap-to-recommendation relevance (manual spot-check / user rating)
- Time from "job found" to "application ready for approval"
- Weekly active use of the progress report
- Zero automated submissions without explicit approval (hard requirement, not just a metric)

## 8. Competitive positioning

Tools like Teal, Simplify, and LazyApply either stop at scoring/tracking or push fully automated blind applications. This project's differentiator is the **transparent multi-agent pipeline with a mandatory human approval checkpoint** — better application quality, and it avoids the ToS and reputational risk that blind auto-apply tools carry.

## 9. Why this project demonstrates strong AI engineering signal

- Multi-agent orchestration (LangGraph), not just a single prompt chain
- RAG grounded in a real, evolving personal knowledge base
- Real external data integration (job APIs) with structuring and ranking, not just Q&A over static docs
- A genuine product decision (human-in-the-loop) driven by real-world constraints, not just technical capability

## 10. Related documents

- `architecture.md` — system design and component breakdown
- `webui.md` — UI/UX design
- `databasedesign.md` — schema design
- `apispecification.md` — API contract
- `security.md` — security and privacy design
- `testing.md` — testing strategy
- `deployment.md` — deployment and infra
