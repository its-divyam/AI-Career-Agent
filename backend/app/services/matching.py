"""Shared matching service used by the sync route AND the Celery task."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.match_runner import run_matching
from app.models.job import Job, JobMatch
from app.models.resume import Resume
from app.agents.job_agent import extract_job_skills
from app.services.analysis import ResumeNotFoundError


class JobNotFoundError(ValueError):
    pass


def job_requirements(job: Job) -> list[str]:
    stored = (job.structured_requirements or {}).get("skills")
    if stored:
        return list(stored)
    return extract_job_skills(job.title or "", job.raw_description or "")


async def run_and_persist_matches(
    session: AsyncSession,
    *,
    user_id: str,
    resume_id: str,
    job_id: str | None = None,
    top_n: int = 20,
) -> dict:
    """Score jobs via the match graph and refresh persisted JobMatches.

    Returns {"matches": [...], "count": n} with JSON-serializable dicts.
    """
    result = await session.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise ResumeNotFoundError(resume_id)
    if not resume.parsed_json:
        from app.services.analysis import ResumeNotParsedError

        raise ResumeNotParsedError(resume_id)

    resume_skills = (resume.parsed_json or {}).get("skills", [])

    job_query = select(Job)
    if job_id:
        job_query = job_query.where(Job.id == job_id)
    jobs = (await session.execute(job_query)).scalars().all()
    if job_id and not jobs:
        raise JobNotFoundError(job_id)

    job_inputs = [{"job_id": str(j.id), "requirements": job_requirements(j)} for j in jobs]
    scored = await run_matching(user_id, str(resume.id), resume_skills, job_inputs, top_n)

    scored_ids = [s["job_id"] for s in scored]
    if scored_ids:
        await session.execute(
            delete(JobMatch).where(
                JobMatch.user_id == user_id, JobMatch.job_id.in_(scored_ids)
            )
        )
    by_id = {str(j.id): j for j in jobs}
    matches = []
    for s in scored:
        session.add(JobMatch(
            user_id=user_id,
            job_id=s["job_id"],
            match_score=s["match_score"],
            match_reasons=s["match_reasons"],
            skill_gap=s["skill_gap"],
        ))
        job = by_id[s["job_id"]]
        reasons = s.get("match_reasons", {})
        matched = reasons.get("matched", [])
        total = reasons.get("total_required", 0)
        matches.append({
            "job_id": s["job_id"],
            "title": job.title,
            "company": job.company,
            "match_score": s["match_score"],
            "match_reasons": [f"{len(matched)} of {total} required skills matched"]
            + [f"Matched: {m}" for m in matched],
            "skill_gap": list((s.get("skill_gap", {}) or {}).get("missing", [])),
        })
    await session.flush()
    return {"matches": matches, "count": len(matches)}
