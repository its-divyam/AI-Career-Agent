from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.skill import SkillGapResult
from app.schemas.skill import SkillGapRequest, SkillGapResponse
from app.utils.dependencies import get_current_user
from app.services.analysis import (
    ResumeNotFoundError,
    ResumeNotParsedError,
    run_and_persist_analysis,
)

router = APIRouter(prefix="/skill-gap", tags=["skill-gap"])


@router.get("")
async def list_skill_gaps(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SkillGapResult).where(SkillGapResult.user_id == user.id).order_by(SkillGapResult.created_at.desc())
    )
    gaps = result.scalars().all()
    return [
        {
            "id": g.id,
            "resume_id": g.resume_id,
            "target_role": g.target_role,
            "have": g.have,
            "missing": g.missing,
            "recommendations": g.recommendations,
            "created_at": g.created_at.isoformat() if g.created_at else None,
        }
        for g in gaps
    ]


@router.post("", response_model=SkillGapResponse)
async def skill_gap(
    body: SkillGapRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Analysis runs on the LangGraph pipeline (retrieve -> ATS -> gap
    # with retry + quality gate) and persists the result. Shape unchanged.
    try:
        gap_result = await run_and_persist_analysis(
            db, user_id=user.id, resume_id=body.resume_id, target_role=body.target_role
        )
    except ResumeNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found")
    except ResumeNotParsedError:
        raise HTTPException(status_code=400, detail="Resume has not been parsed yet")

    return SkillGapResponse(
        have=gap_result["have"],
        missing=gap_result["missing"],
        recommendations=gap_result["recommendations"],
    )
