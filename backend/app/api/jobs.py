import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.job import Job, JobMatch
from app.schemas.job import (
    JobDetail,
    JobIngestRequest,
    JobMatchItem,
    JobSearchResponse,
    MatchRunRequest,
)
from app.utils.dependencies import get_current_user
from app.agents.job_agent import job_requirements
from app.services.analysis import ResumeNotFoundError, ResumeNotParsedError
from app.services.matching import JobNotFoundError, run_and_persist_matches

router = APIRouter(tags=["jobs"])


@router.post("/jobs/ingest", response_model=JobDetail)
async def ingest_job(
    body: JobIngestRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    external_id = body.external_id or uuid.uuid4().hex
    existing = await db.execute(
        select(Job).where(Job.source == body.source, Job.external_id == external_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Job already ingested")

    # LLM extraction with deterministic fallback; never fails the request.
    skills = await job_requirements(body.title, body.raw_description or "")

    job = Job(
        source=body.source,
        external_id=external_id,
        title=body.title,
        company=body.company,
        location=body.location,
        raw_description=body.raw_description,
        structured_requirements={"skills": skills},
    )
    db.add(job)
    await db.flush()

    return JobDetail(
        job_id=str(job.id),
        source=job.source,
        title=job.title,
        company=job.company,
        location=job.location,
        raw_description=job.raw_description,
        structured_requirements=job.structured_requirements,
    )


@router.get("/jobs")
async def list_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).order_by(Job.created_at.desc()))
    return [
        {
            "job_id": str(j.id),
            "source": j.source,
            "title": j.title,
            "company": j.company,
            "location": j.location,
        }
        for j in result.scalars().all()
    ]


@router.get("/jobs/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetail(
        job_id=str(job.id),
        source=job.source,
        title=job.title,
        company=job.company,
        location=job.location,
        raw_description=job.raw_description,
        structured_requirements=job.structured_requirements,
    )


@router.post("/matches/run", response_model=JobSearchResponse)
async def run_matches(
    body: MatchRunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await run_and_persist_matches(
            db,
            user_id=user.id,
            resume_id=body.resume_id,
            job_id=body.job_id,
            top_n=body.top_n,
        )
    except ResumeNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found")
    except ResumeNotParsedError:
        raise HTTPException(status_code=400, detail="Resume has not been parsed yet")
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobSearchResponse(
        status="ok",
        matches=[JobMatchItem(**m) for m in result["matches"]],
    )


@router.get("/matches")
async def list_matches(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobMatch, Job)
        .join(Job, Job.id == JobMatch.job_id)
        .where(JobMatch.user_id == user.id)
        .order_by(JobMatch.match_score.desc())
    )
    items = []
    for match, job in result.all():
        reasons = match.match_reasons or {}
        matched = reasons.get("matched", [])
        total = reasons.get("total_required", 0)
        gap = (match.skill_gap or {}).get("missing", [])
        items.append({
            "match_id": str(match.id),
            "job_id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "match_score": match.match_score,
            "match_reasons": [f"{len(matched)} of {total} required skills matched"]
            + [f"Matched: {m}" for m in matched],
            "skill_gap": list(gap),
            "created_at": match.created_at.isoformat() if match.created_at else None,
        })
    return items
