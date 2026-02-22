from slowapi import Limiter
from slowapi.util import get_remote_address

# Инициализация rate limiter
rate_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],  # Лимит по умолчанию
    storage_uri="memory://",  # Можно использовать redis:// для production
)


# Декораторы для конкретных эндпоинтов
def limit(rate_limit: str):
    """Декоратор для установки лимита на эндпоинт"""
    return rate_limiter.limit(rate_limit)
