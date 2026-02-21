from app.api.auth import router as auth_router
from app.api.employees import router as employees_router
from app.api.departments import router as departments_router
from app.api.positions import router as positions_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.assets import router as assets_router
from app.api.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "employees_router",
    "departments_router",
    "positions_router",
    "projects_router",
    "tasks_router",
    "assets_router",
    "dashboard_router",
]
