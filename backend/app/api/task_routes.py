"""Async task surface: enqueue graph work, poll status.

Contract (same shape in every mode):
  POST -> 202 {"task_id", "status": "PENDING"|"SUCCESS", "result"?}
  GET  -> 200 {"task_id", "status", "result"?|"error"?}

Broker-down behavior: instead of 500ing, the route runs the same shared
service inline and returns SUCCESS immediately. The pipeline never breaks
because Redis is missing.
"""

import uuid
from urllib.parse import urlparse

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.tasks import MatchTaskRequest, SkillGapTaskRequest, TaskStatusResponse
from app.services.analysis import run_and_persist_analysis
from app.services.matching import run_and_persist_matches
from app.tasks.analysis_tasks import analyze_resume_task, match_jobs_task
from app.tasks.celery_app import celery_app
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _broker_reachable(timeout: float = 2.0) -> bool:
    """Fast TCP pre-flight so a dead broker means instant sync fallback."""
    import socket

    parts = urlparse(settings.REDIS_URL)
    if parts.scheme not in ("redis", "rediss"):
        return True
    try:
        with socket.create_connection(
            (parts.hostname or "localhost", parts.port or 6379), timeout=timeout
        ):
            return True
    except OSError:
        return False


async def _require_parsed_resume(db: AsyncSession, user_id: str, resume_id: str) -> None:
    result = await db.execute(
        select(Resume.id, Resume.parsed_json).where(
            Resume.id == resume_id, Resume.user_id == user_id
        )
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not row.parsed_json:
        raise HTTPException(status_code=400, detail="Resume has not been parsed yet")


@router.post("/skill-gap", response_model=TaskStatusResponse, status_code=202)
async def enqueue_skill_gap(
    body: SkillGapTaskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_parsed_resume(db, user.id, body.resume_id)
    if _broker_reachable():
        try:
            async_result = analyze_resume_task.delay(user.id, body.resume_id, body.target_role)
            return TaskStatusResponse(task_id=async_result.id, status="PENDING")
        except Exception:
            pass
    # Broker unavailable: same work, inline, same shape.
    result = await run_and_persist_analysis(
        db, user_id=user.id, resume_id=body.resume_id, target_role=body.target_role
    )
    return TaskStatusResponse(
        task_id=str(uuid.uuid4()),
        status="SUCCESS",
        result={"user_id": user.id, "resume_id": body.resume_id, **result},
    )


@router.post("/matches", response_model=TaskStatusResponse, status_code=202)
async def enqueue_matches(
    body: MatchTaskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_parsed_resume(db, user.id, body.resume_id)
    if _broker_reachable():
        try:
            async_result = match_jobs_task.delay(user.id, body.resume_id, body.job_id, body.top_n)
            return TaskStatusResponse(task_id=async_result.id, status="PENDING")
        except Exception:
            pass
    result = await run_and_persist_matches(
        db, user_id=user.id, resume_id=body.resume_id,
        job_id=body.job_id, top_n=body.top_n,
    )
    return TaskStatusResponse(
        task_id=str(uuid.uuid4()),
        status="SUCCESS",
        result={"user_id": user.id, "resume_id": body.resume_id, **result},
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def task_status(
    task_id: str,
    user: User = Depends(get_current_user),
):
    if not _broker_reachable():
        raise HTTPException(status_code=503, detail="Task backend unavailable")
    try:
        res = AsyncResult(task_id, app=celery_app)
        status = res.status
    except Exception:
        raise HTTPException(status_code=503, detail="Task backend unavailable")

    if status == "SUCCESS":
        payload = res.result or {}
        if not isinstance(payload, dict) or payload.get("user_id") != user.id:
            # Indistinguishable from missing: never leak cross-user results.
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskStatusResponse(task_id=task_id, status=status, result=payload)
    if status == "FAILURE":
        return TaskStatusResponse(task_id=task_id, status=status, error=str(res.result)[:500])
    return TaskStatusResponse(task_id=task_id, status=status)
