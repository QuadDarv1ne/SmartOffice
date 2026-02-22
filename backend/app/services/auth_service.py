"""
Service layer для аутентификации и управления пользователями
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.core.config import settings
from datetime import timedelta
import structlog

logger = structlog.get_logger("smartoffice")


class AuthService:
    """Сервис для управления аутентификацией"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Аутентификация пользователя по email и паролю

        Returns:
            User если успешо, None если нет
        """
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("User not found", email=email)
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning("Invalid password", email=email)
            return None

        if not user.is_active:
            logger.warning("Inactive user login attempt", email=email)
            return None

        logger.info("User authenticated", user_id=user.id, email=email)
        return user

    async def create_user(
        self,
        email: str,
        password: str,
        employee_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> User:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь
        result = await self.db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")

        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            employee_id=employee_id,
            is_admin=is_admin,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User created", user_id=user.id, email=email)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return await self.db.get(User, user_id)

    async def generate_tokens(self, user: User) -> dict:
        """Генерация access и refresh токенов"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "is_admin": user.is_admin,
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_refresh_token(
            data=token_data,
        )

        logger.debug(
            "Tokens generated",
            user_id=user.id,
            access_expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_expires=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        }

    async def refresh_tokens(self, refresh_token: str) -> Optional[dict]:
        """Обновление токенов по refresh токену"""
        payload = verify_refresh_token(refresh_token)

        if not payload:
            logger.warning("Invalid refresh token")
            return None

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Invalid token payload")
            return None

        user = await self.db.get(User, int(user_id))
        if not user:
            logger.warning("User not found", user_id=user_id)
            return None

        if not user.is_active:
            logger.warning("Inactive user token refresh", user_id=user_id)
            return None

        return await self.generate_tokens(user)

    async def deactivate_user(self, user_id: int) -> bool:
        """Деактивация пользователя"""
        user = await self.db.get(User, user_id)
        if not user:
            return False

        user.is_active = False
        await self.db.commit()

        logger.info("User deactivated", user_id=user_id)
        return True
