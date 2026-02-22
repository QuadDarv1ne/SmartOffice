from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    employee_id: Optional[int] = None
    is_admin: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # секунды до истечения access токена


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    employee_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
