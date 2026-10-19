"""Shared analysis service used by the sync route AND the Celery task.

Single implementation so both paths behave identically.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.runner import run_analysis
from app.models.resume import Resume
from app.models.skill import SkillGapResult


class ResumeNotFoundError(ValueError):
    pass


class ResumeNotParsedError(ValueError):
    pass


async def run_and_persist_analysis(
    session: AsyncSession,
    *,
    user_id: str,
    resume_id: str,
    target_role: str,
) -> dict:
    """Run the LangGraph analysis and persist the SkillGapResult.

    Commits are the caller's job (request session commits via get_db;
    tasks commit explicitly). Raises ResumeNotFoundError /
    ResumeNotParsedError for missing data.
    """
    result = await session.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise ResumeNotFoundError(resume_id)
    if not resume.parsed_json:
        raise ResumeNotParsedError(resume_id)

    final = await run_analysis(user_id, target_role, resume.parsed_json, str(resume.id))

    row = SkillGapResult(
        user_id=user_id,
        resume_id=resume.id,
        target_role=target_role,
        have=final.get("have", []),
        missing=final.get("missing", []),
        recommendations=final.get("recommendations", []),
    )
    session.add(row)
    await session.flush()

    return {
        "skill_gap_id": str(row.id),
        "have": row.have,
        "missing": row.missing,
        "recommendations": row.recommendations,
    }
