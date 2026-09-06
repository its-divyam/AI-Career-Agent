import pytest
from app.agents.skill_agent import normalize_skill, get_required_skills, compute_skill_gap


def test_normalize_skill_alias():
    assert normalize_skill("tf") == "TensorFlow"
    assert normalize_skill("pytorch") == "PyTorch"
    assert normalize_skill("sklearn") == "Scikit-learn"
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("k8s") == "Kubernetes"


def test_normalize_skill_passthrough():
    assert normalize_skill("Docker") == "Docker"
    assert normalize_skill("Python") == "Python"
    assert normalize_skill("React") == "React"


def test_get_required_skills_known_role():
    skills = get_required_skills("AI Engineer")
    assert "Python" in skills
    assert "TensorFlow" in skills or "PyTorch" in skills


def test_get_required_skills_unknown_role():
    skills = get_required_skills("Quantum Computing Specialist")
    assert skills == []


@pytest.mark.asyncio
async def test_compute_skill_gap():
    parsed = {
        "skills": ["Python", "Docker", "TensorFlow", "SQL", "React"],
        "experience": [],
        "projects": [],
        "education": [],
    }
    result = await compute_skill_gap(parsed, "AI Engineer")
    assert isinstance(result["have"], list)
    assert isinstance(result["missing"], list)
    assert isinstance(result["recommendations"], list)
    assert "Python" in result["have"]
    assert len(result["have"]) > 0


@pytest.mark.asyncio
async def test_compute_skill_gap_all_skills():
    parsed = {
        "skills": ["Python", "TensorFlow", "PyTorch", "Docker", "SQL",
                    "Machine Learning", "Deep Learning", "Natural Language Processing",
                    "Git", "REST APIs", "RAG", "LangChain", "Vector Databases",
                    "Transformers", "Scikit-learn", "Pandas", "NumPy"],
        "experience": [],
        "projects": [],
        "education": [],
    }
    result = await compute_skill_gap(parsed, "AI Engineer")
    assert len(result["missing"]) <= 3
