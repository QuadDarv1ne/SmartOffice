from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse, RefreshToken

# Rate limiter для auth endpoints
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10 per minute")
async def register(request: Request, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        employee_id=user_data.employee_id,
        is_admin=user_data.is_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("5 per minute")  # Строгий лимит для защиты от brute-force
async def login(request: Request, user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    # Создаем токены
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = create_refresh_token(
        data=token_data,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/token", response_model=Token)
@limiter.limit("5 per minute")
async def login_for_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = create_refresh_token(data=token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/refresh", response_model=Token)
@limiter.limit("10 per minute")
async def refresh_token(request: Request, token_data: RefreshToken, db: AsyncSession = Depends(get_db)):
    """Обновление access токена с помощью refresh токена"""
    
    # Проверяем refresh токен
    payload = verify_refresh_token(token_data.refresh_token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Получаем пользователя
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")
    
    # Создаем новые токены
    new_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
    }
    
    new_access_token = create_access_token(
        data=new_token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    new_refresh_token = create_refresh_token(data=new_token_data)

    logger.info(
        "Token refreshed",
        user_id=user.id,
        email=user.email,
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/logout")
@limiter.limit("10 per minute")
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    """
    Выход из системы
    
    В production здесь можно добавить refresh токен в blacklist
    """
    logger.info("User logged out", user_id=current_user.id, email=current_user.email)
    
    return {"message": "Successfully logged out"}
