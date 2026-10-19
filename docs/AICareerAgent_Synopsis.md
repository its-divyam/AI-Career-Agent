# MINOR PROJECT REPORT (AIML/AIDS-451)

## ON

# AI CAREER AGENT: AN AI-POWERED CAREER ASSISTANT WITH MULTI-AGENT ORCHESTRATION AND HUMAN-IN-THE-LOOP DESIGN

---

## BACHELOR OF TECHNOLOGY
### In
### AIML/ AIDS

## JIMS ENGINEERING MANAGEMENT TECHNICAL CAMPUS
### SESSION 2026-27

---

### By
**DIVYAM GARG**

### Under the guidance of:
**[Guide Name]**

---

## INDEX

**Minor Project Title:** Skillgraph — An AI-Powered Career Assistant with Multi-Agent Orchestration

| S.No | Topic | Page No |
|------|-------|---------|
| 1 | Introduction | 1-2 |
| 2 | Statement of Problem with Objective | 3 |
| 3 | Literature Survey | 4 |
| 4 | Methodology/ Planning of Work | 5 |
| 5 | Software/Hardware Required for Development | 6 |
| 6 | References | 7 |

---

**Student's Signature:** _____________________          **Guide's Signature:** _____________________

---

## 1. Introduction

The modern job market presents a formidable challenge for job seekers, particularly early-career engineers and career switchers. Applying to jobs effectively requires a coordinated effort across multiple dimensions: understanding how one's resume compares to what a target role actually requires, identifying the specific skills that need to be learned or strengthened, and producing tailored application materials (resume reordering, cover letters) for each individual posting. These tasks are time-consuming, repetitive, and cognitively demanding — yet most existing tools address only a single slice of this workflow in isolation.

Skillgraph is an AI-powered career assistant platform designed to address this multifaceted problem. It ingests a user's resume (PDF/DOCX), parses and structures it using Large Language Models (LLMs), computes a detailed skill-gap analysis against a target role using a canonical skills taxonomy, searches for real job postings via legitimate APIs, ranks matches against the user's profile, and drafts tailored application packages — all while maintaining a mandatory human approval checkpoint before any application is submitted.

The system is built around a FastAPI backend with a Next.js frontend, using a multi-agent architecture orchestrated via LangGraph (a stateful graph-based agent framework). The pipeline consists of four specialized agents: (i) a Resume Agent that parses and ATS-scores resumes, (ii) a Job Researcher Agent that fetches, structures, and ranks job postings, (iii) a Skill Agent that computes persistent per-user skill gaps with personalized recommendations, and (iv) an Application Agent that generates tailored resumes and cover letters using Retrieval-Augmented Generation (RAG) over a personal career knowledge base. A human-in-the-loop approval gate ensures that no application is ever submitted without explicit user consent.

The platform is designed to function as a transparent, intelligent career coach: it reads your resume, understands your target role, tells you exactly what's missing, finds real jobs that fit, drafts tailored applications for you to review, and reports back on your progress over time — with the user always retaining full control over the final decision.

## 2. Statement of Problem with Objective

Existing career tools and job-search platforms generally provide only limited, fragmented assistance. Resume scoring tools offer a single ATS score without explaining which specific skills are missing or what projects could close the gap. Job search platforms present vast listings without personalized matching or ranking. Auto-apply tools submit applications blindly without user review, which produces low-quality applications and risks violating job board terms of service. Most critically, no single tool combines resume analysis, skill-gap identification, job matching, and tailored application drafting into one transparent, human-controlled pipeline.

As a result, job seekers are left to manually: (a) compare their resume against dozens of job descriptions, (b) identify which skills they lack, (c) research and select learning resources, (d) tailor their resume and write a cover letter for each application, and (e) track the status of all their applications — all while maintaining quality and consistency across potentially hundreds of applications.

**Objectives:**

1. To design and implement a unified career assistance pipeline capable of ingesting resumes in PDF/DOCX format, parsing them into structured data using LLMs, and computing ATS compatibility scores with specific, actionable feedback.

2. To implement a canonical skills taxonomy (63+ normalized skills with aliases) and compute persistent, per-user skill-gap analyses against target role requirements, providing personalized project and resource recommendations grounded in the identified gaps.

3. To integrate with legitimate job-search APIs (Adzuna/JSearch) to fetch real job postings, structure their requirements using LLMs, and rank matches against the user's resume using vector similarity search and LLM-based re-ranking.

4. To implement a Retrieval-Augmented Generation (RAG) system over a personal career knowledge base, enabling the Application Agent to draft tailored resumes (with reordered bullet points surfacing the most relevant experience) and personalized cover letters for each target job.

5. To enforce a mandatory human-in-the-loop approval gate at every critical decision point, ensuring that no application is submitted without explicit user review and consent, thereby maintaining application quality and avoiding ToS violations.

6. To provide an application tracking system (kanban view: drafted → approved → applied → response received) and auto-generated weekly progress reports that summarize application activity, response rates, and skill-gap closure trends.

7. To design the system so that it can scale to multiple concurrent users through modular agent architecture, background job processing (Celery + Redis), and cost-aware LLM usage (local Ollama for development, hosted APIs for production).

## 3. Literature Survey

Several existing bodies of research and technology directly informed the design of Skillgraph.

**Resume Parsing and ATS Systems:** Applicant Tracking Systems (ATS) have become ubiquitous in modern hiring, with over 98% of Fortune 500 companies using them to filter resumes. Early ATS systems relied on keyword matching and rule-based parsing, which often failed on non-standard resume formats. Recent work has leveraged Large Language Models for more robust resume structuring — extracting contact information, skills, experience, and education into structured JSON representations. Skillgraph builds on this by using LLM-based parsing (via Ollama with Llama 3.2/3.3) that handles diverse resume formats without requiring template-specific parsers, combined with pdfplumber and python-docx for reliable text extraction from PDF and DOCX files.

**Skills Taxonomy and Gap Analysis:** The concept of skill-gap analysis is well-established in organizational learning literature, but personalized, automated skill-gap computation for individual job seekers has seen limited tooling. LinkedIn's "Skills Genome" and similar features provide broad skill assessments but do not compute targeted gaps against specific job requirements. Skillgraph addresses this by maintaining a canonical skills taxonomy of 63+ normalized skills (with aliases such as "TF" → "TensorFlow") and computing set-difference analyses between a user's extracted skills and a target role's requirements, grounded in a seeded mapping that can be edited and extended.

**Multi-Agent AI Systems:** The multi-agent paradigm, where specialized agents collaborate to solve complex tasks, has gained significant traction with frameworks like LangGraph, CrewAI, and AutoGen. LangGraph, developed by LangChain, provides a stateful graph-based orchestration layer that supports branching, looping, and checkpointing — capabilities essential for a career assistant that needs to re-route based on user actions (e.g., re-analyzing skill gaps when a new job is selected). Skillgraph adopts this architecture, with four specialized agents (Resume, Job Researcher, Skill, Application) coordinated by a central orchestrator that maintains shared state and enforces the human approval checkpoint.

**Retrieval-Augmented Generation (RAG):** RAG, introduced by Lewis et al. (2020), combines the strengths of pre-trained language models with external knowledge retrieval, allowing models to generate responses grounded in specific, retrieved documents rather than relying solely on parametric knowledge. Skillgraph applies RAG to the career domain: a vector store (Chroma or Qdrant) indexes the user's past projects, achievements, and career knowledge, and the Application Agent retrieves relevant entries when drafting tailored resumes and cover letters, ensuring that generated content is grounded in the user's actual experience rather than hallucinated.

**Human-in-the-Loop AI:** The importance of human oversight in AI systems, particularly in high-stakes domains like job applications, has been emphasized in recent AI ethics literature. Fully automated job-application tools (e.g., LazyApply, Sonara) submit applications without user review, which both produces low-quality applications and risks violating job board terms of service. Skillgraph explicitly designs the human approval gate as a first-class architectural component — not a UX afterthought — ensuring that the system functions as an intelligent assistant that supports human decision-making rather than replacing it.

**Vector Similarity Search for Matching:** Embedding-based similarity search has become the standard approach for matching unstructured text (e.g., resumes and job descriptions) in modern information retrieval. FAISS (Facebook AI Similarity Search) and vector databases like Chroma and Qdrant enable efficient nearest-neighbor search over high-dimensional embedding vectors. Skillgraph uses vector similarity between resume embeddings and job-description embeddings as a first-pass matching signal, followed by LLM-based re-ranking that considers nuanced factors like recency of experience and skill relevance.

## 4. Methodology/ Planning of Work

1. **Requirement analysis and environment setup:** Defining the canonical skills taxonomy (63+ skills across languages, frameworks, tools, and domains), setting up Python 3.11+, FastAPI, SQLAlchemy (async), SQLite/PostgreSQL, Next.js 15, and the development environment.

2. **Building the Resume Agent:** Implementing PDF/DOCX text extraction using pdfplumber and python-docx, with fallback handling for image-based PDFs. Building an LLM-based structuring pass that converts raw resume text into a structured JSON representation (contact info, skills, experience, projects, education). Implementing ATS compatibility scoring based on keyword density, section structure, formatting checks, and quantified achievement detection.

3. **Building the Skills Taxonomy and Skill Agent:** Seeding a canonical skills taxonomy of 63+ skills with aliases (e.g., "TF" → "TensorFlow", "K8s" → "Kubernetes"). Implementing skill normalization that maps extracted resume skills to canonical taxonomy entries. Computing skill-gap set-difference analyses between user skills and target role requirements. Generating personalized project ideas and learning resources grounded in identified gaps.

4. **Building the Job Researcher Agent:** Integrating with Adzuna and JSearch APIs for legitimate, ToS-compliant job data retrieval. Implementing LLM-based job description structuring (extracting must-have skills, nice-to-haves, seniority level, tools). Computing resume-to-JD embedding similarity for initial ranking, followed by LLM re-ranking for nuanced match scoring.

5. **Building the Application Agent and RAG System:** Setting up a vector store (Chroma/Qdrant) for the personal career knowledge base. Indexing parsed resume data, project descriptions, and user-added achievements. Implementing RAG retrieval to surface relevant past experience when drafting tailored applications. Building the tailored resume reordering and cover letter generation pipeline using LLMs with retrieved context.

6. **Building the Orchestrator (LangGraph):** Implementing the Career Agent as a LangGraph StateGraph with shared state (user profile, resume data, job shortlist, skill gaps, draft applications, approval status). Routing to sub-agents based on user actions and current state. Implementing state persistence/checkpointing so sessions can be resumed.

7. **Building the Human Approval Gate and Application Tracker:** Implementing the approval checkpoint as a mandatory UI step — no code path can reach "applied" status without "approved" first. Building the kanban-style application tracker (drafted → approved → applied → response received). Implementing the auto-generated weekly progress report (Celery Beat scheduled job).

8. **Building the API Layer and Frontend:** Implementing FastAPI route handlers for all endpoints (auth, resume, skill-gap, jobs, applications, reports). Building the Next.js frontend with Tailwind CSS and shadcn/ui: landing page, upload screen, skill-gap dashboard, job matches, application review/approval, tracker, and profile.

9. **Containerization and Testing:** Packaging the full stack with Docker Compose (FastAPI, Next.js, PostgreSQL, Redis, Chroma, Ollama). Writing an automated pytest suite (unit tests for deterministic code, integration tests with mocked LLM/API calls). Testing the human-approval gate explicitly to confirm no bypass path exists.

10. **Documentation and Evaluation:** Recording the architecture, design decisions, and known limitations. Evaluating resume parsing accuracy, skill normalization quality, job matching relevance, and application draft quality against a golden dataset. Documenting security and privacy considerations for handling PII (resumes, career data).

## 5. Software/Hardware Required for the Development of the Project

**Software:**
- Python 3.11+ — primary backend programming language
- FastAPI + Uvicorn — ASGI web framework and server for the backend API
- SQLAlchemy 2.x (async) + Pydantic — ORM and data validation
- SQLite (local dev) / PostgreSQL (production) — relational database for users, resumes, jobs, applications
- Next.js 15 + React 19 + Tailwind CSS — frontend framework, UI library, and styling
- shadcn/ui — pre-built UI components for forms, dialogs, and the approval modal
- LangGraph — stateful, graph-based multi-agent orchestration framework
- Ollama (Llama 3.2/3.3) — local LLM inference for development and low-stakes extraction tasks
- Hosted LLM API (e.g., Claude) — production inference for generation-heavy tasks (cover letters, ranking)
- pdfplumber + python-docx — resume text extraction from PDF and DOCX files
- Chroma or Qdrant — vector database for RAG-based career knowledge base
- Celery + Redis — background job processing (weekly reports, async job-search polling)
- Adzuna / JSearch API — legitimate, ToS-compliant job data sources
- python-jose + bcrypt — JWT authentication and password hashing
- pytest + pytest-asyncio — automated testing
- Docker / Docker Compose — containerization of the full stack
- Git — version control

**Hardware:**
- A development laptop/PC with an NVIDIA GPU (for running Ollama locally with Llama 3.2/3.3 during development)
- Optional cloud GPU (Google Colab / Kaggle) for running heavier embedding and inference tasks when processing large batches
- A minimum of 8 GB RAM and adequate local disk space for model weights, vector store data, and development dependencies

## 6. References

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., and Kiela, D., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," Advances in Neural Information Processing Systems (NeurIPS), Vol. 33, pp. 9459–9474, 2020.

2. Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., Krueger, G., and Sutskever, I., "Learning Transferable Visual Models From Natural Language Supervision," arXiv preprint arXiv:2103.00020, 2021.

3. Johnson, J., Douze, M., and Jégou, H., "Billion-Scale Similarity Search with GPUs," IEEE Transactions on Big Data, Vol. 7, No. 3, pp. 535–547, 2019.

4. Wang, Z., Bovik, A. C., Sheikh, H. R., and Simoncelli, E. P., "Image Quality Assessment: From Error Visibility to Structural Similarity," IEEE Transactions on Image Processing, Vol. 13, No. 4, pp. 600–612, 2004.

5. Schroff, F., Kalenichenko, D., and Philbin, J., "FaceNet: A Unified Embedding for Face Recognition and Clustering," Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pp. 815–823, 2015.

6. Touvron, H., Lavril, T., Izacard, G., Martinet, X., Lachaux, M., Lacroix, T., Rozière, B., Goyal, N., Hambro, E., Azhar, F., Rodriguez, A., Joulin, A., Grave, E., and Lample, G., "LLaMA: Open and Efficient Foundation Language Models," arXiv preprint arXiv:2302.13971, 2023.

7. LangChain Documentation — LangGraph: Stateful Multi-Agent Orchestration, https://langchain-ai.github.io/langgraph/, 2024.

8. Adzuna API Documentation — Job Search API, https://developer.adzuna.com/, 2024.
