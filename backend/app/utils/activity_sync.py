from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile


async def sync_resume_activity(user_id: str, ats_score: int, db: AsyncSession):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        return

    profile.total_resumes += 1
    if profile.best_ats_score is None or ats_score > profile.best_ats_score:
        profile.best_ats_score = ats_score

    _append_activity(profile, "resume", f"Uploaded resume (ATS score: {ats_score})")
    await db.flush()


async def sync_skill_gap_activity(user_id: str, target_role: str, skills_missing: int, db: AsyncSession):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        return

    profile.total_skill_gaps += 1

    progress = profile.skill_progress or {}
    if target_role not in progress:
        progress[target_role] = {"computed": 0, "skills_missing": 0}
    progress[target_role]["computed"] += 1
    progress[target_role]["skills_missing"] = skills_missing
    profile.skill_progress = progress

    _append_activity(profile, "skill_gap", f"Computed skill gap for {target_role} ({skills_missing} skills missing)")
    await db.flush()


async def sync_application_activity(user_id: str, job_title: str, db: AsyncSession):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        return

    profile.total_applications += 1
    _append_activity(profile, "application", f"Created application for {job_title}")
    await db.flush()


def _append_activity(profile: UserProfile, activity_type: str, description: str):
    recent = profile.recent_activity or {"items": []}
    items = recent.get("items", [])
    items.insert(0, {
        "type": activity_type,
        "description": description,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    recent["items"] = items[:20]
    profile.recent_activity = recent
