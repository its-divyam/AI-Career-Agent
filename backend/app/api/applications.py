from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.application import Application
from app.schemas.application import (
    ApplicationCreate,
    ApplicationPatch,
    ApplicationResponse,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])

ALLOWED_STATUSES = {"drafted", "approved", "applied", "withdrawn"}


def _to_response(app: Application) -> ApplicationResponse:
    return ApplicationResponse(
        application_id=str(app.id),
        status=app.status,
        draft_resume=app.draft_resume_json,
        draft_cover_letter=app.draft_cover_letter,
    )


@router.post("", response_model=ApplicationResponse)
async def create_application(
    body: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = (await db.execute(select(Job).where(Job.id == body.job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = (
        await db.execute(
            select(Resume).where(Resume.id == body.resume_id, Resume.user_id == user.id)
        )
    ).scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    app = Application(
        user_id=user.id,
        job_id=job.id,
        resume_id=resume.id,
        resume_version=resume.version,
        status="drafted",
    )
    db.add(app)
    await db.flush()
    return _to_response(app)


@router.get("")
async def list_applications(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application, Job)
        .join(Job, Job.id == Application.job_id)
        .where(Application.user_id == user.id)
        .order_by(Application.created_at.desc())
    )
    return [
        {
            **_to_response(app).model_dump(),
            "job_id": str(job.id),
            "job_title": job.title,
            "company": job.company,
            "created_at": app.created_at.isoformat() if app.created_at else None,
        }
        for app, job in result.all()
    ]


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == application_id, Application.user_id == user.id
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return _to_response(app)


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def patch_application(
    application_id: str,
    body: ApplicationPatch,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == application_id, Application.user_id == user.id
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if body.draft_cover_letter is not None:
        app.draft_cover_letter = body.draft_cover_letter
    if body.draft_resume is not None:
        app.draft_resume_json = body.draft_resume
    if body.status is not None:
        if body.status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUSES)}",
            )
        now = datetime.now(timezone.utc)
        if body.status == "approved" and app.status != "approved":
            app.approved_at = now
        if body.status == "applied" and app.status != "applied":
            app.applied_at = now
        app.status = body.status

    await db.flush()
    return _to_response(app)
