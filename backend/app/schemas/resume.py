from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    resume_id: str
    parsed: dict
    ats_score: int
    ats_flags: list[str]


class ResumeParsed(BaseModel):
    contact: dict | None = None
    skills: list[str] = []
    experience: list[dict] = []
    projects: list[dict] = []
    education: list[dict] = []


class ResumePatch(BaseModel):
    parsed_json: dict | None = None
    target_role: str | None = None
