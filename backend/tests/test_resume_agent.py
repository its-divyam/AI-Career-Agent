import pytest
from app.agents.resume_agent import _compute_ats_score, _fallback_extract


def test_ats_score_full_resume():
    parsed = {
        "contact": {"email": "test@example.com", "phone": "555-1234"},
        "skills": ["Python", "Docker", "SQL", "React", "AWS"],
        "experience": [
            {"title": "Engineer", "company": "ACME", "bullets": ["Built system handling 1M requests/day"]}
        ],
        "education": [{"institution": "MIT", "degree": "BS CS", "year": "2024"}],
        "projects": [],
    }
    score, flags = _compute_ats_score(parsed)
    assert score >= 80
    assert len(flags) <= 1


def test_ats_score_minimal_resume():
    parsed = {
        "contact": {},
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
    }
    score, flags = _compute_ats_score(parsed)
    assert score <= 60
    assert len(flags) >= 3


def test_fallback_extract():
    text = """
John Doe
john@example.com
555-1234

Skills: Python, Docker, SQL

Experience
Software Engineer at ACME
- Built a data pipeline
- Reduced costs by 30%

Education
MIT - B.S. Computer Science - 2024
"""
    parsed = _fallback_extract(text)
    assert "skills" in parsed
    assert "education" in parsed
