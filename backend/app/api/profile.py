from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import ProfileResponse, ProfilePatch
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(user.id, db)
    return _profile_to_response(profile, user)


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    body: ProfilePatch,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(user.id, db)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.flush()
    return _profile_to_response(profile, user)


async def _get_or_create_profile(user_id: str, db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        await db.flush()
    return profile


def _profile_to_response(profile: UserProfile, user: User) -> ProfileResponse:
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        email=user.email,
        display_name=profile.display_name,
        target_role=profile.target_role,
        location=profile.location,
        bio=profile.bio,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        portfolio_url=profile.portfolio_url,
        total_resumes=profile.total_resumes,
        total_skill_gaps=profile.total_skill_gaps,
        total_applications=profile.total_applications,
        total_skills_learned=profile.total_skills_learned,
        best_ats_score=profile.best_ats_score,
        recent_activity=profile.recent_activity,
        skill_progress=profile.skill_progress,
        member_since=profile.created_at.isoformat() if profile.created_at else "",
    )
