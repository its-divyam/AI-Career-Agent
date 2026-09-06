from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    resume_id: str
    job_id: str


class ApplicationPatch(BaseModel):
    draft_cover_letter: str | None = None
    draft_resume: dict | None = None


class ApplicationResponse(BaseModel):
    application_id: str
    status: str
    draft_resume: dict | None = None
    draft_cover_letter: str | None = None
