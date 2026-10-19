import json

from app.config import settings

ROLE_SKILL_MAP = {
    "ai engineer": [
        "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "Natural Language Processing", "Computer Vision", "MLOps", "Docker",
        "SQL", "Git", "REST APIs", "Data Pipelines", "RAG", "LangChain",
        "Vector Databases", "Transformers", "Scikit-learn", "Pandas", "NumPy",
    ],
    "data scientist": [
        "Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas",
        "NumPy", "Scikit-learn", "TensorFlow", "Data Visualization", "Tableau",
        "Jupyter", "A/B Testing", "Feature Engineering", "Big Data", "Spark",
    ],
    "software engineer": [
        "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js",
        "SQL", "Git", "Docker", "AWS", "REST APIs", "Microservices",
        "CI/CD", "Testing", "System Design", "Algorithms", "Data Structures",
    ],
    "frontend engineer": [
        "JavaScript", "TypeScript", "React", "Next.js", "Vue.js", "HTML",
        "CSS", "Tailwind CSS", "Git", "REST APIs", "Testing", "Webpack",
        "Performance Optimization", "Responsive Design", "Accessibility",
    ],
    "backend engineer": [
        "Python", "Java", "Go", "Node.js", "SQL", "PostgreSQL", "Redis",
        "Docker", "AWS", "REST APIs", "GraphQL", "Microservices", "CI/CD",
        "System Design", "Authentication", "Caching",
    ],
    "devops engineer": [
        "Linux", "Docker", "Kubernetes", "AWS", "Terraform", "CI/CD",
        "Jenkins", "GitHub Actions", "Ansible", "Prometheus", "Grafana",
        "Python", "Bash", "Networking", "Security",
    ],
    "ml engineer": [
        "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "MLOps", "Docker", "Kubernetes", "AWS", "MLflow", "Feature Engineering",
        "Data Pipelines", "Model Deployment", "Monitoring", "SQL",
    ],
}

SKILL_ALIASES = {
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "pt": "PyTorch",
    "sklearn": "Scikit-learn",
    "scikit": "Scikit-learn",
    "np": "NumPy",
    "pd": "Pandas",
    "js": "JavaScript",
    "ts": "TypeScript",
    "react.js": "React",
    "reactjs": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "gcp": "Google Cloud Platform",
    "gc": "Google Cloud Platform",
    "k8s": "Kubernetes",
    "gha": "GitHub Actions",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "llm": "Large Language Models",
    "rl": "Reinforcement Learning",
}

CATEGORY_MAP = {
    "Python": "language", "Java": "language", "JavaScript": "language",
    "TypeScript": "language", "Go": "language", "R": "language", "Bash": "language", "SQL": "language",
    "React": "framework", "Next.js": "framework", "Vue.js": "framework", "Node.js": "framework",
    "Django": "framework", "FastAPI": "framework", "Flask": "framework",
    "TensorFlow": "library", "PyTorch": "library", "Scikit-learn": "library",
    "Pandas": "library", "NumPy": "library", "LangChain": "library",
    "Docker": "tool", "Kubernetes": "tool", "Git": "tool", "AWS": "platform",
    "Redis": "tool", "PostgreSQL": "tool", "Jenkins": "tool",
    "Machine Learning": "concept", "Deep Learning": "concept",
    "Natural Language Processing": "concept", "Computer Vision": "concept",
    "MLOps": "concept", "RAG": "concept", "System Design": "concept",
}


CANONICALForms: dict[str, str] = {
    "python": "Python", "java": "Java", "javascript": "JavaScript",
    "typescript": "TypeScript", "go": "Go", "r": "R", "sql": "SQL", "bash": "Bash",
    "react": "React", "next.js": "Next.js", "vue.js": "Vue.js", "node.js": "Node.js",
    "django": "Django", "fastapi": "FastAPI", "flask": "Flask",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "scikit-learn": "Scikit-learn",
    "pandas": "Pandas", "numpy": "NumPy", "langchain": "LangChain",
    "docker": "Docker", "kubernetes": "Kubernetes", "git": "Git", "aws": "AWS",
    "redis": "Redis", "postgresql": "PostgreSQL",
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "natural language processing": "Natural Language Processing",
    "computer vision": "Computer Vision", "mlops": "MLOps", "rag": "RAG",
    "system design": "System Design", "rest apis": "REST APIs",
    "graphql": "GraphQL", "ci/cd": "CI/CD", "microservices": "Microservices",
    "transformers": "Transformers", "vector databases": "Vector Databases",
    "data pipelines": "Data Pipelines", "model deployment": "Model Deployment",
    "statistics": "Statistics", "data visualization": "Data Visualization",
    "a/b testing": "A/B Testing", "feature engineering": "Feature Engineering",
    "big data": "Big Data", "spark": "Spark", "tableau": "Tableau",
    "jupyter": "Jupyter", "terraform": "Terraform", "ansible": "Ansible",
    "prometheus": "Prometheus", "grafana": "Grafana", "linux": "Linux",
    "networking": "Networking", "security": "Security",
    "authentication": "Authentication", "caching": "Caching",
    "monitoring": "Monitoring", "mlflow": "MLflow",
    "github actions": "GitHub Actions", "jenkins": "Jenkins",
}


def normalize_skill(skill_name: str) -> str:
    lower = skill_name.lower().strip()
    if lower in SKILL_ALIASES:
        return SKILL_ALIASES[lower]
    for alias, canonical in SKILL_ALIASES.items():
        if lower == alias.lower():
            return canonical
    if lower in CANONICALForms:
        return CANONICALForms[lower]
    return skill_name.strip()


def get_required_skills(role: str) -> list[str]:
    role_lower = role.lower().strip()
    for key, skills in ROLE_SKILL_MAP.items():
        if key in role_lower or role_lower in key:
            return skills
    return []


async def compute_skill_gap(
    parsed_resume: dict,
    target_role: str,
    context: list[str] | None = None,
) -> dict:
    resume_skills_raw = parsed_resume.get("skills", [])
    resume_skills = set(normalize_skill(s) for s in resume_skills_raw)

    required_skills = get_required_skills(target_role)

    if not required_skills:
        try:
            required_skills = await _llm_extract_role_skills(target_role)
        except Exception:
            required_skills = []

    required_set = set(required_skills)
    have = sorted(resume_skills & required_set)
    missing = sorted(required_set - resume_skills)

    recommendations = await _build_recommendations(missing, target_role, context)

    return {
        "have": have,
        "missing": missing,
        "recommendations": recommendations,
    }


def _static_recommendation(skill: str, target_role: str) -> dict:
    return {
        "skill": skill,
        "project_idea": f"Build a project demonstrating {skill} — e.g. a end-to-end pipeline or feature that showcases practical use of {skill} in a {target_role} context.",
        "resource": f"https://roadmap.sh or search for '{skill} tutorial for {target_role}' on YouTube/courses",
    }


async def _build_recommendations(
    missing: list[str],
    target_role: str,
    context: list[str] | None,
) -> list[dict]:
    """LLM-grounded recommendations when resume context is available.

    Falls back to static templates on any failure or when no context given,
    so existing behavior is preserved byte-for-byte in the default path.
    """
    if not missing:
        return []
    if not context:
        return [_static_recommendation(s, target_role) for s in missing]
    try:
        grounded = await _llm_grounded_recommendations(missing, target_role, context)
        if grounded:
            return grounded
    except Exception:
        pass
    return [_static_recommendation(s, target_role) for s in missing]


async def _llm_grounded_recommendations(
    missing: list[str],
    target_role: str,
    context: list[str],
) -> list[dict]:
    import httpx

    context_block = "\n---\n".join(context)
    prompt = f"""You help a job seeker close skill gaps for a "{target_role}" role.
Their resume excerpts:
{context_block[:3000]}

Missing skills: {", ".join(missing)}

For EACH missing skill, return a JSON array of objects with keys:
- skill: the skill name (exactly as listed)
- project_idea: one concrete project idea building on their background (1-2 sentences)
- resource: one specific high-quality learning resource (name + URL if known)

Return ONLY a valid JSON array, no markdown fences."""

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
        items = json.loads(resp.json()["response"])
        if not isinstance(items, list):
            return []
        valid = []
        for item in items:
            if isinstance(item, dict) and item.get("skill") in missing:
                valid.append({
                    "skill": item["skill"],
                    "project_idea": str(item.get("project_idea", "")),
                    "resource": str(item.get("resource", "")),
                })
        # Fill any skills the LLM skipped with static templates.
        covered = {v["skill"] for v in valid}
        for skill in missing:
            if skill not in covered:
                valid.append(_static_recommendation(skill, target_role))
        return valid


async def _llm_extract_role_skills(role: str) -> list[str]:
    import httpx

    prompt = f"""List the top 15-20 most important technical skills for a "{role}" position.
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
        result = resp.json()
        skills = json.loads(result["response"])
        return [normalize_skill(s) for s in skills] if isinstance(skills, list) else []
