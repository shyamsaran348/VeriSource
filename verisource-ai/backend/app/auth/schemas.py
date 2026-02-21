from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    role: str  # "admin" or "student"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str