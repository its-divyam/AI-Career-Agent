import pytest

from app.agents.resume_agent import _compute_ats_score
from app.agents.skill_agent import compute_skill_gap
from app.graph.runner import build_graph, run_analysis

HEALTHY_PARSED = {
    "contact": {"email": "test@example.com", "phone": "555-1234"},
    "skills": ["Python", "Docker", "SQL", "React", "AWS"],
    "experience": [
        {"title": "Engineer", "company": "ACME", "bullets": ["Built system handling 1M requests/day"]}
    ],
    "education": [{"institution": "MIT", "degree": "BS CS", "year": "2024"}],
    "projects": [],
}

DEGENERATE_PARSED = {
    "contact": {},
    "skills": [],
    "experience": [],
    "projects": [],
    "education": [],
}


async def fake_gap(parsed, role, context):
    direct = await compute_skill_gap(parsed, role, None)
    return direct


async def fake_retrieve(user_id, resume_id, role):
    return [f"ctx:{user_id}:{resume_id}:{role}"]


@pytest.mark.asyncio
async def test_graph_parity_with_direct_calls():
    """Graph output matches calling the agent functions directly."""
    graph = build_graph(retrieve_fn=fake_retrieve, gap_fn=fake_gap)
    final = await run_analysis("u1", "AI Engineer", HEALTHY_PARSED, "r1", graph=graph)

    direct_gap = await compute_skill_gap(HEALTHY_PARSED, "AI Engineer", None)
    direct_score, _ = _compute_ats_score(HEALTHY_PARSED)

    assert final["have"] == direct_gap["have"]
    assert final["missing"] == direct_gap["missing"]
    assert final["recommendations"] == direct_gap["recommendations"]
    assert final["ats_score"] == direct_score
    assert final.get("low_confidence") is not True
    assert final["user_id"] == "u1"
    assert final["resume_id"] == "r1"


@pytest.mark.asyncio
async def test_graph_retries_transient_gap_failure():
    calls = []

    async def flaky_gap(parsed, role, context):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("transient LLM failure")
        return await compute_skill_gap(parsed, role, None)

    graph = build_graph(retrieve_fn=fake_retrieve, gap_fn=flaky_gap)
    final = await run_analysis("u1", "AI Engineer", HEALTHY_PARSED, "r1", graph=graph)

    assert len(calls) == 2
    assert final["gap_attempts"] == 2
    assert final["gap_error"] is None
    assert final["missing"]  # real result, not fallback


@pytest.mark.asyncio
async def test_graph_falls_back_to_review_after_exhausted_retries():
    async def dead_gap(parsed, role, context):
        raise RuntimeError("LLM down")

    graph = build_graph(retrieve_fn=fake_retrieve, gap_fn=dead_gap)
    final = await run_analysis("u1", "AI Engineer", HEALTHY_PARSED, "r1", graph=graph)

    assert final["gap_attempts"] == 2
    assert final["low_confidence"] is True
    # Gap fn dead everywhere: advisory flag still produced, no crash.
    assert any(r["skill"] == "Resume quality check" for r in final["recommendations"])


@pytest.mark.asyncio
async def test_graph_review_uses_static_fallback_when_context_path_fails():
    async def context_only_failure(parsed, role, context):
        if context is not None:
            raise RuntimeError("grounded-LLM failure")
        return await compute_skill_gap(parsed, role, None)

    graph = build_graph(retrieve_fn=fake_retrieve, gap_fn=context_only_failure)
    final = await run_analysis("u1", "AI Engineer", HEALTHY_PARSED, "r1", graph=graph)

    assert final["low_confidence"] is True
    skills = [r["skill"] for r in final["recommendations"]]
    assert "TensorFlow" in skills  # static fallback recs
    assert "Resume quality check" in skills  # plus advisory flag


@pytest.mark.asyncio
async def test_graph_routes_degenerate_parse_to_review():
    graph = build_graph(retrieve_fn=fake_retrieve, gap_fn=fake_gap)
    final = await run_analysis("u1", "AI Engineer", DEGENERATE_PARSED, "r1", graph=graph)

    assert final["low_confidence"] is True
    assert any(r["skill"] == "Resume quality check" for r in final["recommendations"])


@pytest.mark.asyncio
async def test_graph_retrieval_is_scoped_to_user_and_resume():
    seen = {}

    async def spy_retrieve(user_id, resume_id, role):
        seen.update(user_id=user_id, resume_id=resume_id, role=role)
        return None

    graph = build_graph(retrieve_fn=spy_retrieve, gap_fn=fake_gap)
    await run_analysis("user-42", "AI Engineer", HEALTHY_PARSED, "resume-7", graph=graph)

    assert seen == {"user_id": "user-42", "resume_id": "resume-7", "role": "AI Engineer"}


@pytest.mark.asyncio
async def test_graph_retrieval_failure_does_not_fail_run():
    async def broken_retrieve(user_id, resume_id, role):
        raise RuntimeError("chroma down")

    graph = build_graph(retrieve_fn=broken_retrieve, gap_fn=fake_gap)
    final = await run_analysis("u1", "AI Engineer", HEALTHY_PARSED, "r1", graph=graph)

    assert final["rag_context"] is None
    assert final["missing"]
    assert final.get("low_confidence") is not True
