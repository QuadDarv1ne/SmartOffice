from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import structlog

logger = structlog.get_logger("smartoffice")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Глобальный обработчик исключений"""
    
    logger.error(
        "Unhandled exception",
        path=str(request.url.path),
        method=request.method,
        exception_type=type(exc).__name__,
        exception=str(exc),
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "path": str(request.url.path),
        },
    )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    """Обработчик HTTP исключений"""
    
    logger.warning(
        "HTTP exception",
        path=str(request.url.path),
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Обработчик ошибок валидации"""
    
    logger.warning(
        "Validation error",
        path=str(request.url.path),
        method=request.method,
        errors=exc.errors(),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "path": str(request.url.path),
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Обработчик ошибок базы данных"""
    
    logger.error(
        "Database error",
        path=str(request.url.path),
        method=request.method,
        exception_type=type(exc).__name__,
        exception=str(exc),
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "path": str(request.url.path),
        },
    )


async def pydantic_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Обработчик ошибок Pydantic"""
    
    logger.warning(
        "Pydantic validation error",
        path=str(request.url.path),
        method=request.method,
        errors=exc.errors(),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "path": str(request.url.path),
        },
    )
