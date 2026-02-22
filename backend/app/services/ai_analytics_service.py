"""
AI Analytics Service для аналитики и предсказаний

Использует scikit-learn для ML моделей
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import structlog

logger = structlog.get_logger("smartoffice")


class AIAnalyticsService:
    """Сервис для AI аналитики и предсказаний"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_employee_productivity(
        self,
        employee_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Анализ продуктивности сотрудника
        
        Returns:
            Статистика и оценка продуктивности
        """
        from app.models.task import Task
        from app.models.attendance import Attendance
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Задачи сотрудника
        tasks_query = select(Task).where(
            Task.assigned_to == employee_id,
            Task.created_at >= start_date,
        )
        result = await self.db.execute(tasks_query)
        tasks = result.scalars().all()
        
        # Посещаемость
        attendance_query = select(Attendance).where(
            Attendance.employee_id == employee_id,
            Attendance.work_date >= start_date.date(),
        )
        result = await self.db.execute(attendance_query)
        attendance = result.scalars().all()
        
        # Метрики
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        days_present = sum(1 for a in attendance if a.status == 'present')
        attendance_rate = (days_present / days * 100) if days > 0 else 0
        
        # Оценка продуктивности (0-100)
        productivity_score = (completion_rate * 0.6 + attendance_rate * 0.4)
        
        return {
            "employee_id": employee_id,
            "period_days": days,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 2),
            "attendance_rate": round(attendance_rate, 2),
            "productivity_score": round(productivity_score, 2),
            "rating": self._get_rating(productivity_score),
        }
    
    async def predict_task_completion(
        self,
        task_id: int,
    ) -> Dict[str, Any]:
        """
        Предсказание времени завершения задачи
        
        Использует исторические данные для предсказания
        """
        from app.models.task import Task
        
        task = await self.db.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        
        # Получаем исторические данные по похожим задачам
        historical_tasks = await self._get_similar_tasks(task)
        
        if len(historical_tasks) < 3:
            return {
                "task_id": task_id,
                "predicted_days": None,
                "confidence": "low",
                "message": "Недостаточно данных для предсказания",
            }
        
        # Простая линейная регрессия
        X = np.array([[t.estimated_hours or 0] for t in historical_tasks])
        y = np.array([self._calculate_actual_hours(t) for t in historical_tasks])
        
        if len(X) > 0 and len(y) > 0:
            model = LinearRegression()
            model.fit(X, y)
            
            estimated = task.estimated_hours or 0
            predicted_hours = max(0, model.predict([[estimated]])[0])
            
            # Оценка уверенности
            confidence = "high" if len(historical_tasks) >= 10 else "medium"
            
            return {
                "task_id": task_id,
                "predicted_hours": round(predicted_hours, 2),
                "predicted_days": round(predicted_hours / 8, 1),
                "confidence": confidence,
                "based_on_tasks": len(historical_tasks),
            }
        
        return {
            "task_id": task_id,
            "predicted_days": None,
            "confidence": "low",
        }
    
    async def analyze_team_performance(
        self,
        department_id: Optional[int] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Анализ производительности команды/отдела"""
        from app.models.employee import Employee
        from app.models.task import Task
        
        # Получаем сотрудников
        query = select(Employee)
        if department_id:
            query = query.where(Employee.department_id == department_id)
        
        result = await self.db.execute(query)
        employees = result.scalars().all()
        
        # Анализируем каждого
        employee_stats = []
        for emp in employees:
            stats = await self.analyze_employee_productivity(emp.employee_id, days)
            employee_stats.append(stats)
        
        # Агрегированные метрики
        avg_productivity = np.mean([s["productivity_score"] for s in employee_stats]) if employee_stats else 0
        avg_completion = np.mean([s["completion_rate"] for s in employee_stats]) if employee_stats else 0
        
        # Топ сотрудников
        top_performers = sorted(
            employee_stats,
            key=lambda x: x["productivity_score"],
            reverse=True
        )[:5]
        
        return {
            "department_id": department_id,
            "period_days": days,
            "total_employees": len(employees),
            "average_productivity": round(avg_productivity, 2),
            "average_completion_rate": round(avg_completion, 2),
            "top_performers": top_performers,
            "team_rating": self._get_rating(avg_productivity),
        }
    
    async def get_insights(self) -> List[Dict[str, Any]]:
        """
        Генерация AI инсайтов и рекомендаций
        
        Returns:
            Список инсайтов с приоритетами
        """
        insights = []
        
        # Анализ просроченных задач
        from app.models.task import Task
        result = await self.db.execute(
            select(func.count(Task.task_id)).where(
                Task.status != 'completed',
                Task.deadline < datetime.utcnow().date(),
            )
        )
        overdue_tasks = result.scalar() or 0
        
        if overdue_tasks > 5:
            insights.append({
                "type": "warning",
                "category": "tasks",
                "title": "Много просроченных задач",
                "description": f"{overdue_tasks} задач просрочено. Рекомендуется пересмотреть дедлайны.",
                "priority": "high",
                "action": "review_deadlines",
            })
        
        # Анализ загрузки сотрудников
        result = await self.db.execute(
            select(Employee.employee_id, func.count(Task.task_id))
            .join(Task, Task.assigned_to == Employee.employee_id)
            .where(Task.status != 'completed')
            .group_by(Employee.employee_id)
            .having(func.count(Task.task_id) > 10)
        )
        overloaded = result.all()
        
        if overloaded:
            insights.append({
                "type": "warning",
                "category": "workload",
                "title": "Перегруженные сотрудники",
                "description": f"{len(overloaded)} сотрудников имеют более 10 активных задач.",
                "priority": "medium",
                "action": "redistribute_tasks",
            })
        
        # Анализ посещаемости
        from app.models.attendance import Attendance
        result = await self.db.execute(
            select(func.count(Attendance.attendance_id)).where(
                Attendance.status == 'absent',
                Attendance.work_date >= datetime.utcnow().date() - timedelta(days=7),
            )
        )
        absences = result.scalar() or 0
        
        if absences > 10:
            insights.append({
                "type": "info",
                "category": "attendance",
                "title": "Высокая заболеваемость",
                "description": f"{absences} отсутствий за последнюю неделю.",
                "priority": "low",
                "action": "review_health_policies",
            })
        
        logger.info("Generated AI insights", count=len(insights))
        
        return insights
    
    def _get_rating(self, score: float) -> str:
        """Конвертация scores в рейтинг"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "average"
        elif score >= 25:
            return "below_average"
        else:
            return "poor"
    
    def _calculate_actual_hours(self, task) -> float:
        """Расчёт фактических часов задачи"""
        # Заглушка - в реальности нужно считать из time tracking
        return task.estimated_hours or 8.0 if hasattr(task, 'estimated_hours') else 8.0
    
    async def _get_similar_tasks(self, task) -> List[Any]:
        """Получение похожих задач для ML модели"""
        from app.models.task import Task
        
        # Похожие задачи по проекту и приоритету
        query = select(Task).where(
            Task.project_id == task.project_id,
            Task.status == 'completed',
            Task.task_id != task.task_id,
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


def create_ai_analytics_service(db: AsyncSession) -> AIAnalyticsService:
    """Factory для создания сервиса"""
    return AIAnalyticsService(db)
