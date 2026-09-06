from pydantic import BaseModel


class SkillGapRequest(BaseModel):
    resume_id: str
    target_role: str


class SkillRecommendation(BaseModel):
    skill: str
    project_idea: str
    resource: str


class SkillGapResponse(BaseModel):
    have: list[str]
    missing: list[str]
    recommendations: list[SkillRecommendation]
