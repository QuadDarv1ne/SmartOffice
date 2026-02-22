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
    two_factor_code: Optional[str] = None  # TOTP код


class UserLoginResponse(BaseModel):
    requires_2fa: bool  # True если нужен 2FA код
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    temp_token: Optional[str] = None  # Временный токен для 2FA


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # секунды до истечения access токена


class RefreshToken(BaseModel):
    refresh_token: str


class TwoFactorSetup(BaseModel):
    """Схема для настройки 2FA"""
    secret: str
    qr_code: str
    backup_codes: list[str]
    manual_entry_key: str


class TwoFactorConfirm(BaseModel):
    """Схема для подтверждения 2FA"""
    token: str


class TwoFactorDisable(BaseModel):
    """Схема для отключения 2FA"""
    password: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    is_2fa_verified: bool = False


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    employee_id: Optional[int] = None
    two_factor_enabled: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
