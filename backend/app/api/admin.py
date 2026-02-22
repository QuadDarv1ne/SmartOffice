"""
Admin Dashboard API - расширенная статистика и аналитика
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from sqlalchemy.sql import extract
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.employee import Employee, Department, Position
from app.models.project import Project
from app.models.asset import Asset
from app.models.attendance import Attendance

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/stats/overview")
async def get_admin_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    Получение общей статистики системы
    
    Доступно только администраторам
    """
    # Сотрудники
    employees_total = await db.scalar(select(func.count(Employee.employee_id)))
    employees_active = await db.scalar(
        select(func.count(Employee.employee_id)).where(
            Employee.termination_date.is_(None)
        )
    )
    employees_new_this_month = await db.scalar(
        select(func.count(Employee.employee_id)).where(
            extract('month', Employee.hire_date) == datetime.now().month,
            extract('year', Employee.hire_date) == datetime.now().year,
        )
    )

    # Проекты
    projects_total = await db.scalar(select(func.count(Project.project_id)))
    projects_active = await db.scalar(
        select(func.count(Project.project_id)).where(Project.status == 'active')
    )
    projects_completed = await db.scalar(
        select(func.count(Project.project_id)).where(Project.status == 'completed')
    )

    # Отделы
    departments_count = await db.scalar(select(func.count(Department.department_id)))

    # Оборудование
    assets_total = await db.scalar(select(func.count(Asset.asset_id)))
    assets_in_use = await db.scalar(
        select(func.count(Asset.asset_id)).where(Asset.status == 'assigned')
    )
    assets_available = await db.scalar(
        select(func.count(Asset.asset_id)).where(Asset.status == 'available')
    )

    # Посещаемость сегодня
    today = datetime.now().date()
    attendance_today = await db.scalar(
        select(func.count(Attendance.attendance_id)).where(
            Attendance.work_date == today
        )
    )

    return {
        "employees": {
            "total": employees_total,
            "active": employees_active,
            "new_this_month": employees_new_this_month,
        },
        "projects": {
            "total": projects_total,
            "active": projects_active,
            "completed": projects_completed,
        },
        "departments": departments_count,
        "assets": {
            "total": assets_total,
            "in_use": assets_in_use,
            "available": assets_available,
        },
        "attendance_today": attendance_today,
    }


@router.get("/stats/employees")
async def get_employees_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Статистика по сотрудникам"""
    
    # По отделам
    by_department = await db.execute(
        select(
            Department.name,
            func.count(Employee.employee_id).label('count'),
        )
        .join(Employee, isouter=True)
        .group_by(Department.name)
    )
    by_department_result = {row[0]: row[1] for row in by_department.all()}

    # По должностям
    by_position = await db.execute(
        select(
            Position.title,
            func.count(Employee.employee_id).label('count'),
        )
        .join(Employee, isouter=True)
        .group_by(Position.title)
    )
    by_position_result = {row[0]: row[1] for row in by_position.all()}

    # Новые сотрудники по месяцам (за последние 6 месяцев)
    six_months_ago = datetime.now() - timedelta(days=180)
    by_month = await db.execute(
        select(
            extract('year', Employee.hire_date).label('year'),
            extract('month', Employee.hire_date).label('month'),
            func.count(Employee.employee_id).label('count'),
        )
        .where(Employee.hire_date >= six_months_ago)
        .group_by(
            extract('year', Employee.hire_date),
            extract('month', Employee.hire_date),
        )
        .order_by(
            extract('year', Employee.hire_date),
            extract('month', Employee.hire_date),
        )
    )
    by_month_result = [
        {"year": int(row[0]), "month": int(row[1]), "count": row[2]}
        for row in by_month.all()
    ]

    return {
        "by_department": by_department_result,
        "by_position": by_position_result,
        "hiring_trend": by_month_result,
    }


@router.get("/stats/projects")
async def get_projects_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Статистика по проектам"""
    
    # По статусам
    by_status = await db.execute(
        select(
            Project.status,
            func.count(Project.project_id).label('count'),
        )
        .group_by(Project.status)
    )
    by_status_result = {row[0]: row[1] for row in by_status.all()}

    # Бюджет проектов
    total_budget = await db.scalar(
        select(func.sum(Project.budget)).where(Project.budget.isnot(None))
    )
    actual_cost = await db.scalar(
        select(func.sum(Project.actual_cost)).where(Project.actual_cost.isnot(None))
    )

    # Проекты по месяцам создания
    by_month = await db.execute(
        select(
            extract('year', Project.created_at).label('year'),
            extract('month', Project.created_at).label('month'),
            func.count(Project.project_id).label('count'),
        )
        .group_by(
            extract('year', Project.created_at),
            extract('month', Project.created_at),
        )
        .order_by(
            extract('year', Project.created_at),
            extract('month', Project.created_at),
        )
        .limit(6)
    )
    by_month_result = [
        {"year": int(row[0]), "month": int(row[1]), "count": row[2]}
        for row in by_month.all()
    ]

    return {
        "by_status": by_status_result,
        "budget": {
            "total": float(total_budget) if total_budget else 0,
            "spent": float(actual_cost) if actual_cost else 0,
        },
        "creation_trend": by_month_result,
    }


@router.get("/activity/log")
async def get_activity_log(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    Журнал активности пользователей
    
    В реальном приложении данные берутся из audit_log таблицы
    """
    # Заглушка для демонстрации
    return {
        "total": 0,
        "limit": limit,
        "offset": offset,
        "items": [],
    }


@router.get("/system/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    Проверка здоровья системы
    
    Возвращает статус всех компонентов
    """
    import time
    
    start_time = time.time()
    
    # Проверка БД
    try:
        await db.execute(select(1))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Проверка WebSocket
    from app.core.websocket import manager
    ws_stats = manager.get_stats()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "websocket": {
                "status": "healthy",
                "connections": ws_stats,
            },
        },
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }
