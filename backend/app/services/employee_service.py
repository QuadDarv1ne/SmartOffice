"""
Service layer для управления сотрудниками

Этот модуль содержит бизнес-логику для работы с сотрудниками.
Используется в API endpoints для отделения логики от HTTP слоя.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.employee import Employee, Department, Position
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
import structlog

logger = structlog.get_logger("smartoffice")


class EmployeeService:
    """Сервис для управления сотрудниками"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employees(
        self,
        skip: int = 0,
        limit: int = 20,
        department_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        """
        Получение списка сотрудников с пагинацией и фильтрами

        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            department_id: Фильтр по отделу
            search: Поиск по имени

        Returns:
            Кортеж (список сотрудников, общее количество)
        """
        query = select(Employee)

        if department_id:
            query = query.where(Employee.department_id == department_id)

        if search:
            query = query.where(Employee.full_name.ilike(f"%{search}%"))

        # Получаем общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        # Получаем пагинированные результаты
        query = query.offset(skip).limit(limit).order_by(Employee.employee_id)
        result = await self.db.execute(query)
        employees = result.scalars().all()

        logger.debug(
            "Employees retrieved",
            count=len(employees),
            total=total,
            skip=skip,
            limit=limit,
        )

        return list(employees), total

    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Получение сотрудника по ID"""
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.department), selectinload(Employee.position))
            .where(Employee.employee_id == employee_id)
        )
        employee = result.scalar_one_or_none()

        if employee:
            logger.debug("Employee retrieved", employee_id=employee_id)
        else:
            logger.warning("Employee not found", employee_id=employee_id)

        return employee

    async def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        """Создание нового сотрудника"""
        # Проверяем существование отдела и должности
        dept = await self.db.get(Department, employee_data.department_id)
        if not dept:
            raise ValueError("Department not found")

        pos = await self.db.get(Position, employee_data.position_id)
        if not pos:
            raise ValueError("Position not found")

        employee = Employee(**employee_data.model_dump())
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)

        logger.info(
            "Employee created",
            employee_id=employee.employee_id,
            full_name=employee.full_name,
        )

        return employee

    async def update_employee(
        self, employee_id: int, employee_data: EmployeeUpdate
    ) -> Optional[Employee]:
        """Обновление данных сотрудника"""
        employee = await self.db.get(Employee, employee_id)
        if not employee:
            logger.warning("Employee not found for update", employee_id=employee_id)
            return None

        update_data = employee_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)

        await self.db.commit()
        await self.db.refresh(employee)

        logger.info(
            "Employee updated",
            employee_id=employee_id,
            updated_fields=list(update_data.keys()),
        )

        return employee

    async def delete_employee(self, employee_id: int) -> bool:
        """Удаление сотрудника"""
        employee = await self.db.get(Employee, employee_id)
        if not employee:
            logger.warning("Employee not found for deletion", employee_id=employee_id)
            return False

        await self.db.delete(employee)
        await self.db.commit()

        logger.info("Employee deleted", employee_id=employee_id)
        return True

    async def get_employee_stats(self) -> dict:
        """Получение статистики по сотрудникам"""
        # Всего сотрудников
        total_query = select(func.count(Employee.employee_id))
        total = await self.db.scalar(total_query)

        # Активных (без даты увольнения)
        active_query = select(func.count(Employee.employee_id)).where(
            Employee.termination_date.is_(None)
        )
        active = await self.db.scalar(active_query)

        # По отделам
        dept_query = select(
            Department.name, func.count(Employee.employee_id)
        ).join(Employee, isouter=True)
        dept_result = await self.db.execute(dept_query)
        by_department = {row[0]: row[1] for row in dept_result.all()}

        logger.debug("Employee stats retrieved")

        return {
            "total": total or 0,
            "active": active or 0,
            "by_department": by_department,
        }
