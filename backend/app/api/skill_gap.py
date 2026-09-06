from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.skill import SkillGapResult
from app.schemas.skill import SkillGapRequest, SkillGapResponse
from app.utils.dependencies import get_current_user
from app.utils.activity_sync import sync_skill_gap_activity
from app.agents.skill_agent import compute_skill_gap

router = APIRouter(prefix="/skill-gap", tags=["skill-gap"])


@router.post("", response_model=SkillGapResponse)
async def skill_gap(
    body: SkillGapRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == body.resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.parsed_json:
        raise HTTPException(status_code=400, detail="Resume has not been parsed yet")

    gap_result = await compute_skill_gap(resume.parsed_json, body.target_role)

    db_result = SkillGapResult(
        user_id=user.id,
        resume_id=resume.id,
        target_role=body.target_role,
        have=gap_result["have"],
        missing=gap_result["missing"],
        recommendations=gap_result["recommendations"],
    )
    db.add(db_result)
    await db.flush()

    await sync_skill_gap_activity(user.id, body.target_role, len(gap_result["missing"]), db)

    return SkillGapResponse(
        have=gap_result["have"],
        missing=gap_result["missing"],
        recommendations=gap_result["recommendations"],
    )
