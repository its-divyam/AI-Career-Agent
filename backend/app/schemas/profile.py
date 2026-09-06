from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    email: str
    display_name: str | None = None
    target_role: str | None = None
    location: str | None = None
    bio: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    total_resumes: int
    total_skill_gaps: int
    total_applications: int
    total_skills_learned: int
    best_ats_score: int | None = None
    recent_activity: dict | None = None
    skill_progress: dict | None = None
    member_since: str


class ProfilePatch(BaseModel):
    display_name: str | None = None
    target_role: str | None = None
    location: str | None = None
    bio: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
