#!/usr/bin/env python3
"""Seed canonical skills taxonomy into the database."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from app.database import async_session, engine, Base
from app.models.skill import Skill
from app.agents.skill_agent import CATEGORY_MAP, SKILL_ALIASES

SEED_SKILLS = [
    ("Python", ["python3", "py"], "language"),
    ("Java", ["java8", "java11"], "language"),
    ("JavaScript", ["js"], "language"),
    ("TypeScript", ["ts"], "language"),
    ("Go", ["golang"], "language"),
    ("R", [], "language"),
    ("SQL", [], "language"),
    ("Bash", ["shell", "bash scripting"], "language"),
    ("React", ["reactjs", "react.js"], "framework"),
    ("Next.js", ["nextjs"], "framework"),
    ("Vue.js", ["vuejs", "vue"], "framework"),
    ("Node.js", ["nodejs"], "framework"),
    ("Django", [], "framework"),
    ("FastAPI", [], "framework"),
    ("Flask", [], "framework"),
    ("TensorFlow", ["tf"], "library"),
    ("PyTorch", ["pt"], "library"),
    ("Scikit-learn", ["sklearn", "scikit"], "library"),
    ("Pandas", ["pd"], "library"),
    ("NumPy", ["np"], "library"),
    ("LangChain", [], "library"),
    ("Docker", [], "tool"),
    ("Kubernetes", ["k8s"], "tool"),
    ("Git", [], "tool"),
    ("AWS", [], "platform"),
    ("Redis", [], "tool"),
    ("PostgreSQL", ["postgres", "psql"], "tool"),
    ("Machine Learning", ["ml"], "concept"),
    ("Deep Learning", ["dl"], "concept"),
    ("Natural Language Processing", ["nlp"], "concept"),
    ("Computer Vision", ["cv"], "concept"),
    ("MLOps", [], "concept"),
    ("RAG", ["retrieval augmented generation"], "concept"),
    ("System Design", [], "concept"),
    ("REST APIs", ["rest", "restful"], "concept"),
    ("GraphQL", [], "concept"),
    ("CI/CD", ["continuous integration", "continuous deployment"], "concept"),
    ("Microservices", [], "concept"),
    ("Transformers", ["attention mechanism"], "library"),
    ("Vector Databases", ["vectordb"], "tool"),
    ("Data Pipelines", ["etl", "data engineering"], "concept"),
    ("Model Deployment", ["model serving"], "concept"),
    ("Statistics", ["stat"], "concept"),
    ("Data Visualization", ["dataviz", "visualization"], "concept"),
    ("A/B Testing", ["ab testing", "experimentation"], "concept"),
    ("Feature Engineering", ["feature eng"], "concept"),
    ("Big Data", [], "concept"),
    ("Spark", ["pyspark"], "tool"),
    ("Tableau", [], "tool"),
    ("Jupyter", ["jupyter notebook"], "tool"),
    ("Terraform", [], "tool"),
    ("Ansible", [], "tool"),
    ("Prometheus", [], "tool"),
    ("Grafana", [], "tool"),
    ("Linux", [], "tool"),
    ("Networking", ["computer networking"], "concept"),
    ("Security", ["cybersecurity"], "concept"),
    ("Authentication", ["auth"], "concept"),
    ("Caching", ["cache"], "concept"),
    ("Monitoring", ["observability"], "concept"),
    ("MLflow", [], "tool"),
    ("GitHub Actions", ["gha"], "tool"),
    ("Jenkins", [], "tool"),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        for name, aliases, category in SEED_SKILLS:
            result = await session.execute(select(Skill).where(Skill.name == name))
            if result.scalar_one_or_none():
                continue
            skill = Skill(name=name, aliases=aliases, category=category)
            session.add(skill)

        await session.commit()
    print(f"Seeded {len(SEED_SKILLS)} skills.")


if __name__ == "__main__":
    asyncio.run(seed())
