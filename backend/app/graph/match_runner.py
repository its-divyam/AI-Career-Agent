from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.job_agent import score_match


class MatchState(TypedDict, total=False):
    """State for the job-matching graph. No DB access inside nodes."""

    user_id: str
    resume_id: str
    resume_skills: list[str]
    jobs: list[dict]  # each: {job_id, requirements: [...]}
    scored: list[dict]  # each: {job_id, match_score, match_reasons, skill_gap}
    top_n: int


async def score_node(state: MatchState) -> dict:
    scored = []
    for job in state.get("jobs", []):
        score, reasons, gap = score_match(
            state.get("resume_skills", []), job.get("requirements", [])
        )
        scored.append({
            "job_id": job["job_id"],
            "match_score": score,
            "match_reasons": reasons,
            "skill_gap": gap,
        })
    scored.sort(key=lambda m: m["match_score"], reverse=True)
    return {"scored": scored}


async def rank_node(state: MatchState) -> dict:
    top_n = state.get("top_n") or len(state.get("scored", []))
    return {"scored": state.get("scored", [])[:top_n]}


def build_match_graph():
    graph = StateGraph(MatchState)
    graph.add_node("score", score_node)
    graph.add_node("rank", rank_node)
    graph.add_edge(START, "score")
    graph.add_edge("score", "rank")
    graph.add_edge("rank", END)
    return graph.compile()


_match_graph = None


def get_match_graph():
    global _match_graph
    if _match_graph is None:
        _match_graph = build_match_graph()
    return _match_graph


async def run_matching(
    user_id: str,
    resume_id: str,
    resume_skills: list[str],
    jobs: list[dict],
    top_n: int = 20,
    graph=None,
) -> list[dict]:
    """Score + rank jobs. Returns the scored list (persistence is the route's job)."""
    compiled = graph or get_match_graph()
    final = await compiled.ainvoke({
        "user_id": user_id,
        "resume_id": resume_id,
        "resume_skills": resume_skills,
        "jobs": jobs,
        "top_n": top_n,
    })
    return final.get("scored", [])
