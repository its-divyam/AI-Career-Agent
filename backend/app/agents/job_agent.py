"""Job requirement extraction + match scoring.

Baseline is fully deterministic (keyword extraction over the canonical
skill corpus + overlap scoring) so matching works with no LLM. An async
LLM extractor upgrades requirement quality best-effort.
"""

import json
import re

from app.agents.skill_agent import (
    CANONICALForms,
    ROLE_SKILL_MAP,
    SKILL_ALIASES,
    normalize_skill,
)
from app.config import settings

# Searchable corpus: canonical names AND aliases (aliases normalize to
# canonical on match). Longest-first so "Next.js" wins over "js"-style noise.
# "cv"/"gc" excluded: in job posts they almost always mean
# curriculum vitae / garbage collection, not the aliased skills.
_AMBIGUOUS_ALIASES = {"cv", "gc"}
_SKILL_CORPUS: list[str] = sorted(
    {
        *CANONICALForms.values(),
        *(s for skills in ROLE_SKILL_MAP.values() for s in skills),
        *(a for a in SKILL_ALIASES.keys() if a not in _AMBIGUOUS_ALIASES),
    },
    key=len,
    reverse=True,
)


def extract_job_skills(title: str, description: str) -> list[str]:
    """Keyword-extract canonical skills from title + description.

    Deterministic fallback and default path; pure function.
    """
    text = f"{title}\n{description}".lower()
    found: list[str] = []
    for skill in _SKILL_CORPUS:
        name = skill.lower()
        # Short names (R, Go, ...) would match inside unrelated words --
        # require word boundaries for them.
        if len(name) <= 2:
            hit = re.search(r"\b" + re.escape(name) + r"\b", text) is not None
        else:
            hit = name in text
        if hit and normalize_skill(skill) not in found:
            found.append(normalize_skill(skill))
    return found


async def extract_job_skills_llm(title: str, description: str) -> list[str]:
    """LLM requirement extraction. Raises on failure -- callers fall back."""
    import httpx

    prompt = f"""Extract the required technical skills from this job posting.
Job title: {title}
Description:
{description[:3000]}

Return ONLY a JSON array of skill name strings, nothing else.
Example: ["Python", "Docker", "SQL"]"""

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.LLM_BASE_URL}/api/generate",
            json={
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )
        resp.raise_for_status()
        skills = json.loads(resp.json()["response"])
        if not isinstance(skills, list):
            raise ValueError("LLM did not return a list")
        return [normalize_skill(s) for s in skills if isinstance(s, str)]


async def job_requirements(title: str, description: str) -> list[str]:
    """LLM requirements with deterministic fallback. Never raises."""
    try:
        reqs = await extract_job_skills_llm(title, description)
        if reqs:
            return reqs
    except Exception:
        pass
    return extract_job_skills(title, description)


def score_match(resume_skills: list[str], job_skills: list[str]) -> tuple[float, dict, dict]:
    """Score overlap between normalized resume skills and job requirements.

    Returns (score 0-100, match_reasons dict, skill_gap dict).
    Pure function.
    """
    have = {normalize_skill(s) for s in resume_skills}
    reqs: list[str] = []
    for skill in job_skills:
        norm = normalize_skill(skill)
        if norm not in reqs:
            reqs.append(norm)

    matched = [r for r in reqs if r in have]
    missing = [r for r in reqs if r not in have]
    score = round(100.0 * len(matched) / len(reqs), 1) if reqs else 0.0

    return (
        score,
        {"matched": matched, "total_required": len(reqs)},
        {"missing": missing},
    )
