from pydantic import BaseModel


class JobSearchRequest(BaseModel):
    resume_id: str
    target_role: str
    location: str = ""
    filters: dict = {}


class JobMatchItem(BaseModel):
    job_id: str
    title: str
    company: str | None = None
    match_score: float
    match_reasons: list[str] = []
    skill_gap: list[str] = []


class JobSearchResponse(BaseModel):
    status: str
    matches: list[JobMatchItem]


class JobDetail(BaseModel):
    job_id: str
    source: str
    title: str
    company: str | None = None
    location: str | None = None
    raw_description: str | None = None
    structured_requirements: dict | None = None


class JobIngestRequest(BaseModel):
    source: str = "manual"
    external_id: str | None = None
    title: str
    company: str | None = None
    location: str | None = None
    raw_description: str | None = None


class MatchRunRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    top_n: int = 20
