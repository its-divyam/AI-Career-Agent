from pydantic import BaseModel


class SkillGapTaskRequest(BaseModel):
    resume_id: str
    target_role: str


class MatchTaskRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    top_n: int = 20


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None
