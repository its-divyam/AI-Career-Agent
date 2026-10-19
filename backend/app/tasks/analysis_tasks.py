"""Celery tasks wrapping the shared services.

Tasks own their DB session (workers are separate processes) and return
JSON-serializable payloads that always include user_id for ownership
checks on the status endpoint.
"""

import asyncio
import concurrent.futures

from app.database import async_session as _default_session_maker
from app.services.analysis import run_and_persist_analysis
from app.services.matching import run_and_persist_matches
from app.tasks.celery_app import celery_app

# Indirection so tests can point tasks at a throwaway DB.
session_maker = _default_session_maker


def _run_coro(coro):
    """Drive a coroutine from sync task code.

    asyncio.run() in the common case; a fresh thread when already inside
    a running loop (eager .apply() in async tests).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


@celery_app.task(bind=True, name="career.analyze_resume")
def analyze_resume_task(self, user_id: str, resume_id: str, target_role: str) -> dict:
    async def _run() -> dict:
        async with session_maker() as session:
            try:
                result = await run_and_persist_analysis(
                    session, user_id=user_id, resume_id=resume_id, target_role=target_role
                )
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return {"user_id": user_id, "resume_id": resume_id, **result}

    return _run_coro(_run())


@celery_app.task(bind=True, name="career.match_jobs")
def match_jobs_task(
    self,
    user_id: str,
    resume_id: str,
    job_id: str | None = None,
    top_n: int = 20,
) -> dict:
    async def _run() -> dict:
        async with session_maker() as session:
            try:
                result = await run_and_persist_matches(
                    session, user_id=user_id, resume_id=resume_id,
                    job_id=job_id, top_n=top_n,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return {"user_id": user_id, "resume_id": resume_id, **result}

    return _run_coro(_run())
