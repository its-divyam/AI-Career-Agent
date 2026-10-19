import json
import io
import re

import pdfplumber
from docx import Document

from app.config import settings


async def parse_resume(content: bytes, file_ext: str) -> tuple[dict, int, list[str]]:
    raw_text = _extract_text(content, file_ext)
    parsed = await _llm_structure(raw_text)
    ats_score, ats_flags = _compute_ats_score(parsed)
    return parsed, ats_score, ats_flags


def _extract_text(content: bytes, file_ext: str) -> str:
    if file_ext == "pdf":
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_ext == "docx":
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file extension: {file_ext}")


def extract_text(content: bytes, file_ext: str) -> str:
    """Public wrapper for raw text extraction (used by RAG indexing)."""
    return _extract_text(content, file_ext)


async def _llm_structure(raw_text: str) -> dict:
    try:
        import httpx

        prompt = f"""Extract structured information from this resume text.
Return a JSON object with these fields:
- contact: object with name, email, phone, location, linkedin (strings or null)
- skills: array of skill strings
- experience: array of objects with title, company, duration, bullets (array of strings)
- projects: array of objects with name, description, tech_stack (array of strings)
- education: array of objects with institution, degree, year

Resume text:
{raw_text[:4000]}

Return ONLY valid JSON, no markdown fences."""

        async with httpx.AsyncClient(timeout=60) as client:
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
            result = resp.json()
            return json.loads(result["response"])
    except Exception:
        return _fallback_extract(raw_text)


def _fallback_extract(text: str) -> dict:
    lines = text.strip().split("\n")
    contact = {}
    skills = []
    experience = []
    projects = []
    education = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        lower = line_stripped.lower()
        if "@" in line_stripped and not any(c.isdigit() for c in line_stripped):
            contact["email"] = line_stripped
        elif any(kw in lower for kw in ["university", "college", "institute", "bachelor", "master", "phd", "b.s.", "m.s."]):
            education.append({"institution": line_stripped, "degree": "", "year": ""})
        elif any(kw in lower for kw in ["experience", "employment", "work history"]):
            continue
        elif len(line_stripped.split()) <= 8 and not line_stripped.endswith("."):
            skills.append(line_stripped)

    return {
        "contact": contact,
        "skills": skills[:30],
        "experience": experience,
        "projects": projects,
        "education": education,
    }


def _compute_ats_score(parsed: dict) -> tuple[int, list[str]]:
    score = 50
    flags = []

    if parsed.get("contact", {}).get("email"):
        score += 10
    else:
        flags.append("missing contact email")

    if parsed.get("contact", {}).get("phone"):
        score += 5

    skills = parsed.get("skills", [])
    if len(skills) >= 5:
        score += 10
    elif len(skills) > 0:
        score += 5
    else:
        flags.append("no skills listed")

    experience = parsed.get("experience", [])
    if len(experience) >= 1:
        score += 10
    else:
        flags.append("no work experience listed")

    if parsed.get("education"):
        score += 5
    else:
        flags.append("no education section")

    for exp in experience:
        bullets = exp.get("bullets", [])
        has_quant = any(re.search(r"\d+", b) for b in bullets)
        if has_quant:
            score += 2
            break
    else:
        flags.append("missing quantified achievements")

    if not any("summary" in str(parsed.get("contact", "")).lower() for _ in [1]):
        flags.append("no summary section")

    return min(score, 100), flags
