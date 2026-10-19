from typing import TypedDict


class CareerState(TypedDict, total=False):
    """Shared state for the career-analysis graph.

    Carries user/resume scoping end-to-end so every downstream node
    (retrieval today, job matching in Stage 4) stays per-user isolated.
    """

    user_id: str
    resume_id: str | None
    target_role: str
    parsed: dict | None

    rag_context: list[str] | None

    ats_score: int | None
    ats_flags: list[str]

    have: list[str]
    missing: list[str]
    recommendations: list[dict]

    gap_attempts: int
    gap_error: str | None
    low_confidence: bool
