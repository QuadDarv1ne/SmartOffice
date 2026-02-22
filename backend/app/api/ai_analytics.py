"""
AI Analytics API для аналитики и предсказаний
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.services.ai_analytics_service import AIAnalyticsService, create_ai_analytics_service

router = APIRouter(prefix="/ai/analytics", tags=["AI Analytics"])


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIAnalyticsService:
    """Factory для получения AIAnalyticsService"""
    return create_ai_analytics_service(db)


@router.get("/employee/{employee_id}/productivity")
async def get_employee_productivity(
    employee_id: int,
    days: int = Query(30, ge=1, le=365),
    service: AIAnalyticsService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
):
    """Анализ продуктивности сотрудника"""
    return await service.analyze_employee_productivity(employee_id, days)


@router.get("/task/{task_id}/prediction")
async def predict_task_completion(
    task_id: int,
    service: AIAnalyticsService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
):
    """Предсказание времени завершения задачи"""
    try:
        return await service.predict_task_completion(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/team/performance")
async def get_team_performance(
    department_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    service: AIAnalyticsService = Depends(get_ai_service),
    current_user: User = Depends(get_current_admin),  # Только админы
):
    """Анализ производительности команды"""
    return await service.analyze_team_performance(department_id, days)


@router.get("/insights")
async def get_ai_insights(
    service: AIAnalyticsService = Depends(get_ai_service),
    current_user: User = Depends(get_current_admin),
):
    """
    AI инсайты и рекомендации
    
    Анализирует данные и генерирует рекомендации
    """
    return await service.get_insights()


@router.get("/dashboard")
async def get_ai_dashboard(
    service: AIAnalyticsService = Depends(get_ai_service),
    current_user: User = Depends(get_current_admin),
):
    """
    AI Dashboard с ключевыми метриками
    """
    from app.models.employee import Employee
    from app.models.task import Task
    from app.models.project import Project
    from sqlalchemy import select, func
    
    # Базовая статистика
    employees_count = await service.db.scalar(select(func.count(Employee.employee_id)))
    active_projects = await service.db.scalar(
        select(func.count(Project.project_id)).where(Project.status == 'active')
    )
    
    # Продуктивность
    team_perf = await service.analyze_team_performance(days=30)
    
    # Инсайты
    insights = await service.get_insights()
    
    return {
        "summary": {
            "total_employees": employees_count,
            "active_projects": active_projects,
            "team_productivity": team_perf.get("average_productivity", 0),
        },
        "insights": insights,
        "top_performers": team_perf.get("top_performers", [])[:3],
    }
