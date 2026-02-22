"""
Service layer - бизнес-логика приложения

Этот пакет содержит сервисы для отделения бизнес-логики от API endpoints.
"""

from app.services.employee_service import EmployeeService
from app.services.auth_service import AuthService

__all__ = [
    "EmployeeService",
    "AuthService",
]
