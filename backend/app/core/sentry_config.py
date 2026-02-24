"""
Sentry конфигурация для мониторинга ошибок
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from pydantic_settings import BaseSettings
import structlog

logger = structlog.get_logger("smartoffice")


class SentrySettings(BaseSettings):
    """Настройки Sentry"""
    
    SENTRY_DSN: str = ""  # DSN из Sentry проекта
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% запросов для tracing
    SENTRY_ERRORS_SAMPLE_RATE: float = 1.0  # 100% ошибок
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


def init_sentry():
    """Инициализация Sentry"""
    settings = SentrySettings()
    
    if not settings.SENTRY_DSN:
        logger.warning("Sentry DSN not configured, monitoring disabled")
        return
    
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            error_sample_rate=settings.SENTRY_ERRORS_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(
                    level=None,  # Standard logging
                    event_level=None,  # Don't send logs as events
                ),
            ],
            
            # Настройки для production
            send_default_pii=True,  # Отправлять user data (осторожно в production!)
            max_breadcrumbs=50,
            
            # Фильтры
            before_send=lambda event, hint: filter_sensitive_data(event, hint),
        )
        
        logger.info(
            "Sentry initialized",
            dsn=settings.SENTRY_DSN[:20] + "...",
            environment=settings.SENTRY_ENVIRONMENT,
        )
        
    except Exception as e:
        logger.error("Failed to initialize Sentry", error=str(e))


def filter_sensitive_data(event: dict, hint: dict) -> dict | None:
    """
    Фильтрация чувствительных данных перед отправкой в Sentry
    
    Returns:
        event или None (если не нужно отправлять)
    """
    # Не отправляем события с определёнными ошибками
    if 'exception' in event:
        exception_type = event['exception']['values'][0].get('type', '')
        
        # Игнорируем некоторые типы ошибок
        if exception_type in ['HTTPException', 'ValidationError']:
            return None
    
    # Удаляем чувствительные данные из request
    if 'request' in event:
        request = event['request']
        
        # Удаляем cookies
        if 'cookies' in request:
            del request['cookies']
        
        # Удаляем Authorization header
        if 'headers' in request:
            headers = request['headers']
            if 'Authorization' in headers:
                headers['Authorization'] = '[REDACTED]'
    
    # Удаляем чувствительные данные из пользователя
    if 'user' in event:
        user = event.get('user', {})
        # Оставляем только ID, удаляем email и другие данные
        if 'email' in user:
            user['email'] = '[REDACTED]'
    
    return event


def set_sentry_user(user_id: int, email: str, is_admin: bool = False):
    """Установка пользователя в Sentry context"""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "is_admin": is_admin,
    })


def add_sentry_breadcrumb(category: str, message: str, level: str = "info", data: dict = None):
    """Добавление breadcrumb в Sentry"""
    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level,
        data=data or {},
    )


# Auto-init on import
init_sentry()
