import logging
import sys
from pathlib import Path

import structlog
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json или console
    LOG_FILE: str = "logs/app.log"


logging_settings = LoggingSettings()


def setup_logging():
    """Настройка структурированного логирования"""
    
    # Создаем директорию для логов
    log_file = Path(logging_settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Уровень логирования
    log_level = getattr(logging, logging_settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Конфигурация logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        stream=sys.stdout,
    )
    
    # Файловый хендлер
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    
    # Консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Настройка structlog
    if logging_settings.LOG_FORMAT == "json":
        # JSON формат для production
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    else:
        # Console формат для разработки
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Получаем logger
    logger = structlog.get_logger("smartoffice")
    
    logger.info(
        "Logging initialized",
        log_level=logging_settings.LOG_LEVEL,
        log_format=logging_settings.LOG_FORMAT,
        log_file=str(log_file),
    )
    
    return logger


def get_logger(name: str = "smartoffice"):
    """Получить logger для использования в модулях"""
    return structlog.get_logger(name)


# Инициализируем логирование при импорте
logger = setup_logging()
