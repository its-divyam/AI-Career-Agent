"""Graph construction + runner. Parallel path: routes still call agent
functions directly until parity is proven (then they switch to run_analysis).
"""

from langgraph.graph import END, START, StateGraph

from app.graph import nodes
from app.graph.state import CareerState
from app.rag.store import query_resume_chunks


async def _default_retrieve(user_id: str, resume_id: str, target_role: str):
    if not resume_id:
        return None
    try:
        return await query_resume_chunks(
            user_id, resume_id, f"{target_role} skills experience projects"
        ) or None
    except Exception:
        return None


def build_graph(
    *,
    retrieve_fn=_default_retrieve,
    ats_fn=nodes._compute_ats_score,
    gap_fn=nodes.compute_skill_gap,
):
    graph = StateGraph(CareerState)

    async def retrieve(state: CareerState) -> dict:
        return await nodes.retrieve_node(state, retrieve_fn=retrieve_fn)

    async def ats(state: CareerState) -> dict:
        return await nodes.ats_node(state, ats_fn=ats_fn)

    async def gap(state: CareerState) -> dict:
        return await nodes.gap_node(state, gap_fn=gap_fn)

    async def review(state: CareerState) -> dict:
        return await nodes.review_node(state, gap_fn=gap_fn)

    graph.add_node("retrieve", retrieve)
    graph.add_node("ats", ats)
    graph.add_node("gap", gap)
    graph.add_node("review", review)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "ats")
    graph.add_edge("ats", "gap")
    graph.add_conditional_edges(
        "gap",
        nodes.route_after_gap,
        {"gap": "gap", "review": "review", "end": END},
    )
    graph.add_edge("review", END)

    return graph.compile()


_default_graph = None


def get_graph():
    global _default_graph
    if _default_graph is None:
        _default_graph = build_graph()
    return _default_graph


async def run_analysis(
    user_id: str,
    target_role: str,
    parsed: dict,
    resume_id: str | None = None,
    graph=None,
) -> dict:
    """Run the full analysis graph. Returns the final CareerState."""
    compiled = graph or get_graph()
    return await compiled.ainvoke({
        "user_id": user_id,
        "resume_id": resume_id,
        "target_role": target_role,
        "parsed": parsed,
    })
