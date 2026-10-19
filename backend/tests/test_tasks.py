"""Tests for Celery tasks + task routes.

Task logic runs via .apply() (no broker needed). Broker-down behavior is
simulated deterministically so tests pass with or without Redis running.
"""

from types import SimpleNamespace

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401 -- register all tables
import app.tasks.analysis_tasks as tasks_mod
import app.api.task_routes as task_routes
import app.services.analysis as analysis_svc
from app.database import Base, get_db
from app.main import app
from app.models.job import Job, JobMatch
from app.models.resume import Resume
from app.models.skill import SkillGapResult
from app.models.user import User
from app.services.analysis import ResumeNotFoundError
from app.utils.dependencies import get_current_user


async def fake_run_analysis(user_id, target_role, parsed, resume_id=None):
    return {
        "have": ["Python"],
        "missing": ["Docker"],
        "recommendations": [{"skill": "Docker", "project_idea": "p", "resource": "r"}],
    }


@pytest.fixture
async def api(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/test.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as s:
        s.add(User(id="user-a", email="a@t.t", hashed_password="x"))
        s.add(User(id="user-b", email="b@t.t", hashed_password="x"))
        s.add(Resume(
            id="resume-a",
            user_id="user-a",
            parsed_json={"skills": ["Python", "Docker", "SQL"]},
            ats_score=70,
            target_role="AI Engineer",
        ))
        s.add(Job(
            id="job-1",
            source="test",
            external_id="j1",
            title="AI Engineer",
            company="Acme",
            structured_requirements={"skills": ["Python", "Docker", "PyTorch"]},
        ))
        await s.commit()

    async def override_db():
        async with Session() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    current = {"id": "user-a"}
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=current["id"])
    monkeypatch.setattr(tasks_mod, "session_maker", Session)
    # Hermetic: stub the graph runner (graph itself is covered in test_graph.py).
    monkeypatch.setattr(analysis_svc, "run_analysis", fake_run_analysis)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client, current, Session

    app.dependency_overrides.clear()
    await engine.dispose()


async def test_analyze_task_persists_and_returns_payload(api):
    _, _, Session = api
    result = tasks_mod.analyze_resume_task.apply(
        args=("user-a", "resume-a", "AI Engineer")
    ).get()
    assert result["user_id"] == "user-a"
    assert result["have"] == ["Python"]
    assert result["missing"] == ["Docker"]

    async with Session() as s:
        rows = (await s.execute(
            select(SkillGapResult).where(SkillGapResult.user_id == "user-a")
        )).scalars().all()
        assert len(rows) == 1
        assert rows[0].target_role == "AI Engineer"


async def test_analyze_task_missing_resume_raises(api):
    with pytest.raises(ResumeNotFoundError):
        tasks_mod.analyze_resume_task.apply(args=("user-a", "nope", "AI Engineer")).get()


async def test_match_task_scores_and_persists(api):
    _, _, Session = api
    result = tasks_mod.match_jobs_task.apply(args=("user-a", "resume-a", None, 20)).get()
    assert result["count"] == 1
    assert result["matches"][0]["match_score"] == pytest.approx(66.7, abs=0.05)

    async with Session() as s:
        rows = (await s.execute(
            select(JobMatch).where(JobMatch.user_id == "user-a")
        )).scalars().all()
        assert len(rows) == 1


async def test_enqueue_falls_back_to_sync_when_broker_down(api, monkeypatch):
    client, _, _ = api

    def dead_delay(*args, **kwargs):
        raise ConnectionError("redis down")

    monkeypatch.setattr(task_routes.analyze_resume_task, "delay", dead_delay)

    r = await client.post(
        "/tasks/skill-gap", json={"resume_id": "resume-a", "target_role": "AI Engineer"}
    )
    assert r.status_code == 202, r.text
    body = r.json()
    assert body["status"] == "SUCCESS"
    assert body["result"]["have"] == ["Python"]
    # Work was still persisted.
    assert len((await client.get("/skill-gap")).json()) == 1


async def test_match_enqueue_falls_back_to_sync_when_broker_down(api, monkeypatch):
    client, _, _ = api

    def dead_delay(*args, **kwargs):
        raise ConnectionError("redis down")

    monkeypatch.setattr(task_routes.match_jobs_task, "delay", dead_delay)

    r = await client.post("/tasks/matches", json={"resume_id": "resume-a"})
    assert r.status_code == 202, r.text
    assert r.json()["status"] == "SUCCESS"
    assert r.json()["result"]["count"] == 1
    assert len((await client.get("/matches")).json()) == 1


async def test_status_endpoint_503_without_backend(api, monkeypatch):
    client, _, _ = api

    class Boom:
        def __init__(self, *args, **kwargs):
            raise ConnectionError("redis down")

    monkeypatch.setattr(task_routes, "AsyncResult", Boom)
    r = await client.get("/tasks/whatever")
    assert r.status_code == 503


async def test_status_success_enforces_ownership(api, monkeypatch):
    client, current, _ = api

    class FakeResult:
        def __init__(self, task_id, app=None):
            self._id = task_id

        @property
        def status(self):
            return "SUCCESS"

        @property
        def result(self):
            return {"user_id": "user-a", "have": ["Python"]}

    monkeypatch.setattr(task_routes, "AsyncResult", FakeResult)
    monkeypatch.setattr(task_routes, "_broker_reachable", lambda *a, **k: True)

    r = await client.get("/tasks/abc")
    assert r.status_code == 200
    assert r.json()["result"]["have"] == ["Python"]

    current["id"] = "user-b"
    r = await client.get("/tasks/abc")
    assert r.status_code == 404
