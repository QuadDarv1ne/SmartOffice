from app.api.auth import router as auth_router
from app.api.employees import router as employees_router
from app.api.departments import router as departments_router
from app.api.positions import router as positions_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.assets import router as assets_router
from app.api.dashboard import router as dashboard_router
from app.api.websocket import router as websocket_router
from app.api.admin import router as admin_router
from app.api.health import router as health_router
from app.api.files import router as files_router
from app.api.two_factor import router as two_factor_router
from app.api.audit_log import router as audit_log_router
from app.api.task_comments import router as task_comments_router
from app.api.graphql_api import router as graphql_router
from app.api.metrics import router as metrics_router
from app.api.ai_analytics import router as ai_analytics_router
from app.api.saml import router as saml_router

__all__ = [
    "auth_router",
    "employees_router",
    "departments_router",
    "positions_router",
    "projects_router",
    "tasks_router",
    "assets_router",
    "dashboard_router",
    "websocket_router",
    "admin_router",
    "health_router",
    "files_router",
    "two_factor_router",
    "audit_log_router",
    "task_comments_router",
    "graphql_router",
    "metrics_router",
    "ai_analytics_router",
    "saml_router",
]
