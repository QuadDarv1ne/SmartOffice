from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import structlog

logger = structlog.get_logger("smartoffice")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание access токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug("Access token created", exp=expire.isoformat())
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание refresh токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug("Refresh token created", exp=expire.isoformat())
    return encoded_jwt


def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """
    Декодирование токена
    
    Args:
        token: JWT токен
        expected_type: Ожидаемый тип токена (access или refresh)
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        
        # Проверка типа токена
        token_type = payload.get("type")
        if token_type != expected_type:
            logger.warning(
                "Token type mismatch",
                expected=expected_type,
                actual=token_type,
            )
            return None
        
        return payload
    except JWTError as e:
        logger.warning("Token decode error", error=str(e))
        return None


def verify_refresh_token(refresh_token: str) -> Optional[dict]:
    """Проверка refresh токена"""
    return decode_token(refresh_token, expected_type="refresh")


def verify_access_token(access_token: str) -> Optional[dict]:
    """Проверка access токена"""
    return decode_token(access_token, expected_type="access")
