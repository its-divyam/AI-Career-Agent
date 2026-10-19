"""Endpoint tests for jobs/matches/applications with per-user isolation.

Uses a throwaway SQLite DB + dependency overrides (no JWT, no network).
"""

from types import SimpleNamespace

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.api.jobs as jobs_api
import app.models  # noqa: F401 -- register all tables
from app.agents.job_agent import extract_job_skills
from app.database import Base, get_db
from app.main import app
from app.models.resume import Resume
from app.models.user import User
from app.utils.dependencies import get_current_user

JOB = {
    "source": "test",
    "external_id": "job-1",
    "title": "AI Engineer",
    "company": "Acme",
    "location": "Remote",
    "raw_description": "Looking for Python and Docker. PyTorch experience required.",
}


@pytest.fixture
async def api(tmp_path, monkeypatch):
    async def deterministic_requirements(title: str, description: str) -> list[str]:
        return extract_job_skills(title, description)

    # Pin keyword extraction: tests must not depend on a live Ollama.
    monkeypatch.setattr(jobs_api, "job_requirements", deterministic_requirements)

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

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client, current

    app.dependency_overrides.clear()
    await engine.dispose()


async def test_ingest_extracts_skills_and_rejects_duplicates(api):
    client, _ = api
    r = await client.post("/jobs/ingest", json=JOB)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["structured_requirements"]["skills"] == ["PyTorch", "Python", "Docker"] or \
        set(body["structured_requirements"]["skills"]) == {"Python", "Docker", "PyTorch"}

    r = await client.post("/jobs/ingest", json=JOB)
    assert r.status_code == 409


async def test_match_run_scores_and_persists(api):
    client, _ = api
    await client.post("/jobs/ingest", json=JOB)

    r = await client.post("/matches/run", json={"resume_id": "resume-a"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert len(body["matches"]) == 1
    match = body["matches"][0]
    assert match["title"] == "AI Engineer"
    # resume has Python+Docker of {PyTorch, Python, Docker} -> 66.7
    assert match["match_score"] == pytest.approx(66.7, abs=0.05)
    assert "PyTorch" in match["skill_gap"]

    r = await client.get("/matches")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["match_score"] == pytest.approx(66.7, abs=0.05)

    # Re-run refreshes instead of duplicating.
    await client.post("/matches/run", json={"resume_id": "resume-a"})
    assert len((await client.get("/matches")).json()) == 1


async def test_matches_are_user_isolated(api):
    client, current = api
    await client.post("/jobs/ingest", json=JOB)
    await client.post("/matches/run", json={"resume_id": "resume-a"})

    current["id"] = "user-b"
    assert (await client.get("/matches")).json() == []

    # user-b cannot match against user-a's resume (indistinguishable from missing).
    r = await client.post("/matches/run", json={"resume_id": "resume-a"})
    assert r.status_code == 404


async def test_applications_crud_and_isolation(api):
    client, current = api
    job_id = (await client.post("/jobs/ingest", json=JOB)).json()["job_id"]

    r = await client.post("/applications", json={"job_id": job_id, "resume_id": "resume-a"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "drafted"
    app_id = r.json()["application_id"]

    r = await client.patch(f"/applications/{app_id}", json={"status": "approved"})
    assert r.status_code == 200
    assert r.json()["status"] == "approved"

    r = await client.patch(f"/applications/{app_id}", json={"status": "hired"})
    assert r.status_code == 400

    r = await client.get("/applications")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["job_title"] == "AI Engineer"

    current["id"] = "user-b"
    assert (await client.get("/applications")).json() == []
    r = await client.get(f"/applications/{app_id}")
    assert r.status_code == 404
    # user-b cannot apply with user-a's resume.
    r = await client.post("/applications", json={"job_id": job_id, "resume_id": "resume-a"})
    assert r.status_code == 404
