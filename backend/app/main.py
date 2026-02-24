from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog

# Инициализация Sentry
from app.core.sentry_config import init_sentry, set_sentry_user

init_sentry()

# Prometheus middleware (will be added after app creation)
from app.middleware.prometheus import PrometheusMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import logger
from app.core.limiter import rate_limiter
from app.core.exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    pydantic_exception_handler,
)
from app.api import (
    auth_router,
    employees_router,
    departments_router,
    positions_router,
    projects_router,
    tasks_router,
    assets_router,
    dashboard_router,
    websocket_router,
    admin_router,
    health_router,
    files_router,
    two_factor_router,
    audit_log_router,
    task_comments_router,
    graphql_router,
    metrics_router,
    ai_analytics_router,
    saml_router,
)


# Инициализация rate limiter
# (use application-level rate_limiter from app.core.limiter)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application startup", app_name=settings.APP_NAME)
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Добавляем rate limiter
app.state.limiter = rate_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(
        "Request started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown",
    )
    
    response = await call_next(request)
    
    logger.debug(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    
    return response


# Регистрация обработчиков исключений
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, pydantic_exception_handler)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(departments_router, prefix="/api")
app.include_router(positions_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(assets_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(two_factor_router, prefix="/api")
app.include_router(audit_log_router, prefix="/api")
app.include_router(task_comments_router, prefix="/api")
app.include_router(graphql_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(ai_analytics_router, prefix="/api")
app.include_router(saml_router, prefix="/api")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Логирование при старте
logger.info(
    "Application routes registered",
    routes=[route.path for route in app.routes],
)
