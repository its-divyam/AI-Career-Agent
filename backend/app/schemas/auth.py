from pydantic import BaseModel, EmailStr


class AuthSignup(BaseModel):
    email: EmailStr
    password: str


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    access_token: str
    token_type: str = "bearer"
