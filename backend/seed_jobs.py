#!/usr/bin/env python3
"""Seed demo job postings (global catalog, no user data). Idempotent."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select

from app.agents.job_agent import extract_job_skills
from app.database import async_session
from app.models.job import Job

JOBS = [
    {
        "source": "demo",
        "external_id": "demo-ai-eng",
        "title": "AI Engineer",
        "company": "NeuralWorks",
        "location": "Remote",
        "raw_description": (
            "Build LLM features with Python, LangChain, and RAG over vector databases. "
            "Serve models with Docker, PyTorch, and Transformers. MLOps experience a plus."
        ),
    },
    {
        "source": "demo",
        "external_id": "demo-ds",
        "title": "Data Scientist",
        "company": "InsightLabs",
        "location": "Bengaluru",
        "raw_description": (
            "Own experimentation and modeling with Python, SQL, Pandas, Scikit-learn. "
            "A/B testing, Tableau dashboards, and Spark for large datasets."
        ),
    },
    {
        "source": "demo",
        "external_id": "demo-swe",
        "title": "Software Engineer",
        "company": "ShipIt",
        "location": "Remote",
        "raw_description": (
            "Full-stack product work: TypeScript, React, Node.js, PostgreSQL, REST APIs. "
            "CI/CD with GitHub Actions, AWS deployments, testing with Jest."
        ),
    },
    {
        "source": "demo",
        "external_id": "demo-backend",
        "title": "Backend Engineer",
        "company": "LedgerLine",
        "location": "Hybrid",
        "raw_description": (
            "Design microservices in Python and Go. PostgreSQL, Redis caching, GraphQL, "
            "Docker, authentication, and system design for scale."
        ),
    },
    {
        "source": "demo",
        "external_id": "demo-devops",
        "title": "DevOps Engineer",
        "company": "CloudNine",
        "location": "Remote",
        "raw_description": (
            "Own Kubernetes clusters on AWS with Terraform. CI/CD via Jenkins and GitHub "
            "Actions. Prometheus, Grafana, Linux, Bash, and Python automation."
        ),
    },
    {
        "source": "demo",
        "external_id": "demo-frontend",
        "title": "Frontend Engineer",
        "company": "PixelPerfect",
        "location": "Remote",
        "raw_description": (
            "Craft responsive UIs with React, Next.js, TypeScript, and Tailwind CSS. "
            "Accessibility, performance optimization, and REST API integration."
        ),
    },
]


async def main() -> None:
    async with async_session() as session:
        added = 0
        for spec in JOBS:
            existing = await session.execute(
                select(Job).where(
                    Job.source == spec["source"], Job.external_id == spec["external_id"]
                )
            )
            if existing.scalar_one_or_none():
                continue
            skills = extract_job_skills(spec["title"], spec["raw_description"])
            session.add(Job(
                source=spec["source"],
                external_id=spec["external_id"],
                title=spec["title"],
                company=spec["company"],
                location=spec["location"],
                raw_description=spec["raw_description"],
                structured_requirements={"skills": skills},
            ))
            added += 1
        await session.commit()
        print(f"Seeded {added} jobs.")


if __name__ == "__main__":
    asyncio.run(main())
