from app.agents.job_agent import extract_job_skills, score_match


def test_extract_job_skills_finds_canonical_names():
    skills = extract_job_skills(
        "Senior AI Engineer",
        "We need Python and Docker experience. Bonus: Kubernetes, pytorch, and sklearn.",
    )
    assert "Python" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "PyTorch" in skills  # alias normalized
    assert "Scikit-learn" in skills  # alias normalized


def test_extract_job_skills_empty_description():
    assert extract_job_skills("Mystery Role", "") == []


def test_score_match_full_overlap():
    score, reasons, gap = score_match(
        ["Python", "Docker", "SQL"], ["Python", "Docker"]
    )
    assert score == 100.0
    assert reasons["matched"] == ["Python", "Docker"]
    assert gap["missing"] == []


def test_score_match_partial_overlap():
    score, reasons, gap = score_match(
        ["Python", "React"], ["Python", "Docker", "SQL", "AWS"]
    )
    assert score == 25.0
    assert reasons["matched"] == ["Python"]
    assert reasons["total_required"] == 4
    assert gap["missing"] == ["Docker", "SQL", "AWS"]


def test_score_match_no_overlap():
    score, reasons, gap = score_match(["React"], ["Python", "Docker"])
    assert score == 0.0
    assert reasons["matched"] == []
    assert gap["missing"] == ["Python", "Docker"]


def test_score_match_empty_requirements():
    score, reasons, gap = score_match(["Python"], [])
    assert score == 0.0
    assert gap["missing"] == []


def test_score_match_normalizes_aliases():
    score, _, _ = score_match(["k8s", "js"], ["Kubernetes", "JavaScript"])
    assert score == 100.0
