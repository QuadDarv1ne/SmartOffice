from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserLoginResponse, Token, UserResponse, RefreshToken
from app.api.deps import get_current_user
from app.services.auth_service import AuthService
from app.services.two_factor_service import TwoFactorAuthService
from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog

logger = structlog.get_logger("smartoffice")

# Rate limiter для auth endpoints
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Factory для получения AuthService"""
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10 per minute")
async def register(
    request: Request,
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    """Регистрация нового пользователя"""
    try:
        user = await service.create_user(
            email=user_data.email,
            password=user_data.password,
            employee_id=user_data.employee_id,
            is_admin=user_data.is_admin,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=UserLoginResponse)
@limiter.limit("5 per minute")  # Строгий лимит для защиты от brute-force
async def login(
    request: Request,
    user_data: UserLogin,
    service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Вход в систему
    
    Если включен 2FA и код не предоставлен, возвращает requires_2fa=True
    """
    user = await service.authenticate_user(user_data.email, user_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Проверяем 2FA
    if user.two_factor_enabled:
        # Если 2FA включен, но код не предоставлен
        if not user_data.two_factor_code:
            # Возвращаем временный токен для второго шага
            from app.core.security import create_access_token
            temp_token = create_access_token(
                data={"sub": str(user.id), "type": "2fa_temp"},
                expires_delta=timedelta(minutes=5),  # 5 минут на ввод кода
            )
            
            return UserLoginResponse(
                requires_2fa=True,
                temp_token=temp_token,
            )
        
        # Проверяем 2FA код
        two_factor_service = TwoFactorAuthService(db)
        if not await two_factor_service.verify_2fa_token(user.id, user_data.two_factor_code):
            raise HTTPException(
                status_code=401,
                detail="Invalid 2FA code",
            )

    # Если 2FA не включен или успешно пройден
    tokens = await service.generate_tokens(user)

    logger.info(
        "User logged in",
        user_id=user.id,
        email=user.email,
    )

    return UserLoginResponse(
        requires_2fa=False,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )


@router.post("/token", response_model=Token)
@limiter.limit("5 per minute")
async def login_for_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    """Вход через OAuth2 форму (для совместимости)"""
    user = await service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tokens = await service.generate_tokens(user)

    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )


@router.post("/refresh", response_model=Token)
@limiter.limit("10 per minute")
async def refresh_token(
    request: Request,
    token_data: RefreshToken,
    service: AuthService = Depends(get_auth_service),
):
    """Обновление access токена с помощью refresh токена"""
    tokens = await service.refresh_tokens(token_data.refresh_token)

    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )


@router.post("/logout")
@limiter.limit("10 per minute")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Выход из системы

    В production здесь можно добавить refresh токен в blacklist
    """
    logger.info("User logged out", user_id=current_user.id, email=current_user.email)

    return {"message": "Successfully logged out"}
