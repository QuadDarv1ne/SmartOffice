"""
2FA Service для двухфакторной аутентификации

Использует TOTP (Time-based One-Time Password) алгоритм
"""

import pyotp
import qrcode
import io
import base64
import json
import secrets
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.user import User

logger = structlog.get_logger("smartoffice")


class TwoFactorAuthService:
    """Сервис для управления 2FA"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def generate_secret(self) -> str:
        """Генерация нового секрета для 2FA"""
        return pyotp.random_base32()
    
    def get_provisioning_uri(self, email: str, secret: str, issuer: str = "SmartOffice") -> str:
        """Генерация URI для настройки в приложении аутентификации"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """
        Генерация QR кода в base64
        
        Returns:
            base64 строка с изображением QR кода
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем в base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """
        Проверка TOTP токена
        
        Args:
            secret: Секрет пользователя
            token: 6-значный код из приложения
        
        Returns:
            True если токен валиден
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # valid_window=1 позволяет ±30 секунд
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """Генерация backup кодов для восстановления доступа"""
        codes = []
        for _ in range(count):
            # Генерируем код формата XXXX-XXXX
            code = f"{secrets.randbelow(10000):04d}-{secrets.randbelow(10000):04d}"
            codes.append(code)
        return codes
    
    async def enable_2fa(self, user_id: int) -> dict:
        """
        Включение 2FA для пользователя
        
        Returns:
            dict с secret, qr_code и backup_codes
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Генерируем новый секрет
        secret = self.generate_secret()
        provisioning_uri = self.get_provisioning_uri(user.email, secret)
        qr_code = self.generate_qr_code(provisioning_uri)
        backup_codes = self.generate_backup_codes()
        
        # Сохраняем секрет (но ещё не активируем)
        user.two_factor_secret = secret
        user.two_factor_enabled = False  # Активируем после подтверждения
        user.backup_codes = json.dumps(backup_codes)
        
        await self.db.commit()
        
        logger.info("2FA setup initiated", user_id=user_id, email=user.email)
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "manual_entry_key": secret,
        }
    
    async def confirm_2fa(self, user_id: int, token: str) -> bool:
        """
        Подтверждение включения 2FA
        
        Args:
            user_id: ID пользователя
            token: TOTP код из приложения
        
        Returns:
            True если успешно
        """
        user = await self.db.get(User, user_id)
        if not user or not user.two_factor_secret:
            return False
        
        # Проверяем токен
        if not self.verify_totp(user.two_factor_secret, token):
            return False
        
        # Активируем 2FA
        user.two_factor_enabled = True
        user.two_factor_verified = True
        
        await self.db.commit()
        
        logger.info("2FA enabled", user_id=user_id, email=user.email)
        
        return True
    
    async def disable_2fa(self, user_id: int, password_verified: bool = False) -> bool:
        """
        Отключение 2FA
        
        Args:
            user_id: ID пользователя
            password_verified: True если пароль уже подтверждён
        
        Returns:
            True если успешно
        """
        user = await self.db.get(User, user_id)
        if not user:
            return False
        
        user.two_factor_enabled = False
        user.two_factor_verified = False
        user.two_factor_secret = None
        user.backup_codes = None
        
        await self.db.commit()
        
        logger.info("2FA disabled", user_id=user_id, email=user.email)
        
        return True
    
    async def verify_2fa_token(self, user_id: int, token: str) -> bool:
        """
        Проверка 2FA токена при входе
        
        Args:
            user_id: ID пользователя
            token: TOTP или backup код
        
        Returns:
            True если успешно
        """
        user = await self.db.get(User, user_id)
        if not user or not user.two_factor_enabled:
            return True  # 2FA не включен
        
        # Проверяем как TOTP
        if self.verify_totp(user.two_factor_secret or "", token):
            return True
        
        # Проверяем как backup код
        if user.backup_codes:
            backup_codes = json.loads(user.backup_codes)
            if token in backup_codes:
                # Удаляем использованный код
                backup_codes.remove(token)
                user.backup_codes = json.dumps(backup_codes)
                await self.db.commit()
                logger.info("Backup code used", user_id=user_id)
                return True
        
        return False
    
    async def regenerate_backup_codes(self, user_id: int) -> list[str]:
        """Перегенерация backup кодов"""
        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        new_codes = self.generate_backup_codes()
        user.backup_codes = json.dumps(new_codes)
        await self.db.commit()
        
        logger.info("Backup codes regenerated", user_id=user_id)
        
        return new_codes


# Helper функции
def create_2fa_service(db: AsyncSession) -> TwoFactorAuthService:
    """Factory для создания сервиса"""
    return TwoFactorAuthService(db)
