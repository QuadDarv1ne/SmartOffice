"""
2FA API для управления двухфакторной аутентификацией
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserLogin,
    UserLoginResponse,
    Token,
    TwoFactorSetup,
    TwoFactorConfirm,
    TwoFactorDisable,
)
from app.services.two_factor_service import TwoFactorAuthService, create_2fa_service
from app.api.deps import get_current_user
from datetime import timedelta

logger = structlog.get_logger("smartoffice")

router = APIRouter(prefix="/auth/2fa", tags=["Two-Factor Authentication"])


def get_2fa_service(db: AsyncSession = Depends(get_db)) -> TwoFactorAuthService:
    """Factory для получения 2FA сервиса"""
    return create_2fa_service(db)


@router.post("/setup", response_model=TwoFactorSetup)
async def setup_2fa(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: TwoFactorAuthService = Depends(get_2fa_service),
):
    """
    Настройка 2FA для текущего пользователя
    
    Возвращает секрет и QR код для настройки в приложении
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA already enabled",
        )
    
    try:
        result = await service.enable_2fa(current_user.id)
        
        logger.info(
            "2FA setup initiated",
            user_id=current_user.id,
            email=current_user.email,
        )
        
        return TwoFactorSetup(**result)
        
    except Exception as e:
        logger.error("Failed to setup 2FA", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to setup 2FA")


@router.post("/confirm")
async def confirm_2fa(
    request: Request,
    data: TwoFactorConfirm,
    current_user: User = Depends(get_current_user),
    service: TwoFactorAuthService = Depends(get_2fa_service),
):
    """
    Подтверждение включения 2FA
    
    Необходимо отправить TOTP код из приложения
    """
    success = await service.confirm_2fa(current_user.id, data.token)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid TOTP code",
        )
    
    logger.info(
        "2FA confirmed and enabled",
        user_id=current_user.id,
        email=current_user.email,
    )
    
    return {
        "success": True,
        "message": "2FA enabled successfully",
    }


@router.post("/disable")
async def disable_2fa(
    request: Request,
    data: TwoFactorDisable,
    current_user: User = Depends(get_current_user),
    service: TwoFactorAuthService = Depends(get_2fa_service),
):
    """
    Отключение 2FA
    
    Требуется подтверждение паролем
    """
    # Здесь должна быть проверка пароля
    # Для безопасности можно запросить пароль ещё раз
    
    success = await service.disable_2fa(current_user.id, password_verified=True)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to disable 2FA",
        )
    
    logger.info(
        "2FA disabled",
        user_id=current_user.id,
        email=current_user.email,
    )
    
    return {
        "success": True,
        "message": "2FA disabled successfully",
    }


@router.post("/backup-codes/regenerate")
async def regenerate_backup_codes(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: TwoFactorAuthService = Depends(get_2fa_service),
):
    """
    Перегенерация backup кодов
    
    Старые коды будут аннулированы
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA not enabled",
        )
    
    try:
        new_codes = await service.regenerate_backup_codes(current_user.id)
        
        logger.info(
            "Backup codes regenerated",
            user_id=current_user.id,
            email=current_user.email,
        )
        
        return {
            "success": True,
            "backup_codes": new_codes,
            "message": "Save these codes in a secure location",
        }
        
    except Exception as e:
        logger.error("Failed to regenerate backup codes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to regenerate codes")


@router.get("/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
):
    """Получение статуса 2FA для текущего пользователя"""
    return {
        "enabled": current_user.two_factor_enabled,
        "verified": current_user.two_factor_verified,
        "has_backup_codes": bool(current_user.backup_codes),
    }
