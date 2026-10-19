"""Graph nodes. Each wraps an existing agent/RAG function -- no logic rewrites.

Dependencies are injectable parameters so tests can run the graph
hermetically (no Ollama/Chroma). Production wiring lives in runner.py.
"""

from app.agents.resume_agent import _compute_ats_score
from app.agents.skill_agent import compute_skill_gap
from app.graph.state import CareerState

MAX_GAP_ATTEMPTS = 2
ATS_LOW_CONFIDENCE = 40


async def retrieve_node(state: CareerState, *, retrieve_fn) -> dict:
    """Best-effort RAG context. Never fails the graph."""
    try:
        chunks = await retrieve_fn(
            state["user_id"], state.get("resume_id") or "", state["target_role"]
        )
        return {"rag_context": chunks or None}
    except Exception:
        return {"rag_context": None}


async def ats_node(state: CareerState, *, ats_fn=_compute_ats_score) -> dict:
    score, flags = ats_fn(state.get("parsed") or {})
    return {"ats_score": score, "ats_flags": flags}


async def gap_node(state: CareerState, *, gap_fn=compute_skill_gap) -> dict:
    attempts = state.get("gap_attempts", 0) + 1
    try:
        result = await gap_fn(
            state.get("parsed") or {},
            state["target_role"],
            state.get("rag_context"),
        )
        return {
            "have": result["have"],
            "missing": result["missing"],
            "recommendations": result["recommendations"],
            "gap_attempts": attempts,
            "gap_error": None,
        }
    except Exception as exc:
        return {"gap_attempts": attempts, "gap_error": str(exc)}


async def review_node(state: CareerState, *, gap_fn=compute_skill_gap) -> dict:
    """Low-confidence fallback: static recommendations + advisory flag.

    Re-runs the gap function WITHOUT context, which is the deterministic
    static-template path, then marks the run for human review.
    """
    result = {"have": [], "missing": [], "recommendations": []}
    try:
        result = await gap_fn(state.get("parsed") or {}, state["target_role"], None)
    except Exception:
        pass
    advisory = {
        "skill": "Resume quality check",
        "project_idea": (
            "Your resume parsed with low confidence (low ATS score or no "
            "detectable skills). Consider re-uploading a clearer PDF/DOCX, "
            "then re-running the analysis."
        ),
        "resource": "https://roadmap.sh",
    }
    return {
        "have": result.get("have", []),
        "missing": result.get("missing", []),
        "recommendations": [*result.get("recommendations", []), advisory],
        "low_confidence": True,
        "gap_error": None,
    }


def route_after_gap(state: CareerState) -> str:
    """Retry on transient failure, else quality-gate to review or finish."""
    if state.get("gap_error") and state.get("gap_attempts", 0) < MAX_GAP_ATTEMPTS:
        return "gap"
    parsed = state.get("parsed") or {}
    # Zero skill overlap means either an unrelated resume or a bad parse --
    # both deserve human review rather than silent template output.
    no_overlap = not state.get("have")
    low_ats = (state.get("ats_score") or 0) < ATS_LOW_CONFIDENCE
    no_skills = not (parsed.get("skills") or [])
    if no_overlap or (low_ats and no_skills):
        return "review"
    return "end"
