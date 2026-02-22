"""
GraphQL Schema для SmartOffice

Использует Strawberry GraphQL для type-safe GraphQL API
"""

from __future__ import annotations
import strawberry
from typing import List, Optional
from datetime import datetime
from strawberry.scalars import JSON


@strawberry.type
class User:
    id: int
    email: str
    is_active: bool
    is_admin: bool
    employee_id: Optional[int]
    created_at: datetime


@strawberry.type
class Employee:
    employee_id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    hire_date: datetime
    department_id: int
    position_id: int
    manager_id: Optional[int]
    personnel_number: Optional[str]


@strawberry.type
class Department:
    department_id: int
    name: str
    manager_id: Optional[int]
    created_at: datetime


@strawberry.type
class Position:
    position_id: int
    title: str
    min_salary: Optional[float]
    max_salary: Optional[float]


@strawberry.type
class Project:
    project_id: int
    name: str
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: str
    budget: Optional[float]


@strawberry.type
class Task:
    task_id: int
    project_id: int
    title: str
    description: Optional[str]
    assigned_to: Optional[int]
    deadline: Optional[datetime]
    priority: str
    status: str
    created_at: datetime


@strawberry.type
class Asset:
    asset_id: int
    name: str
    type: str
    serial_number: Optional[str]
    status: str
    purchase_price: Optional[float]


@strawberry.type
class DashboardStats:
    employees_total: int
    employees_active: int
    projects_total: int
    projects_active: int
    tasks_total: int
    tasks_pending: int
    assets_total: int


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from SmartOffice GraphQL API!"
    
    @strawberry.field
    async def employees(self, info: strawberry.Info, limit: int = 100, offset: int = 0) -> List[Employee]:
        """Получение списка сотрудников"""
        from app.core.database import async_session_maker
        from app.models.employee import Employee as EmployeeModel
        
        async with async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(EmployeeModel).offset(offset).limit(limit)
            )
            employees = result.scalars().all()
            
            return [
                Employee(
                    employee_id=e.employee_id,
                    full_name=e.full_name,
                    email=e.email,
                    phone=e.phone,
                    hire_date=e.hire_date,
                    department_id=e.department_id,
                    position_id=e.position_id,
                    manager_id=e.manager_id,
                    personnel_number=e.personnel_number,
                )
                for e in employees
            ]
    
    @strawberry.field
    async def employee(self, info: strawberry.Info, employee_id: int) -> Optional[Employee]:
        """Получение сотрудника по ID"""
        from app.core.database import async_session_maker
        from app.models.employee import Employee as EmployeeModel
        
        async with async_session_maker() as session:
            employee = await session.get(EmployeeModel, employee_id)
            
            if not employee:
                return None
            
            return Employee(
                employee_id=employee.employee_id,
                full_name=employee.full_name,
                email=employee.email,
                phone=employee.phone,
                hire_date=employee.hire_date,
                department_id=employee.department_id,
                position_id=employee.position_id,
                manager_id=employee.manager_id,
                personnel_number=employee.personnel_number,
            )
    
    @strawberry.field
    async def departments(self, info: strawberry.Info) -> List[Department]:
        """Получение списка отделов"""
        from app.core.database import async_session_maker
        from app.models.employee import Department as DepartmentModel
        
        async with async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(DepartmentModel))
            departments = result.scalars().all()
            
            return [
                Department(
                    department_id=d.department_id,
                    name=d.name,
                    manager_id=d.manager_id,
                    created_at=d.created_at,
                )
                for d in departments
            ]
    
    @strawberry.field
    async def projects(self, info: strawberry.Info, status: Optional[str] = None) -> List[Project]:
        """Получение списка проектов"""
        from app.core.database import async_session_maker
        from app.models.project import Project as ProjectModel
        
        async with async_session_maker() as session:
            from sqlalchemy import select
            query = select(ProjectModel)
            if status:
                query = query.where(ProjectModel.status == status)
            
            result = await session.execute(query)
            projects = result.scalars().all()
            
            return [
                Project(
                    project_id=p.project_id,
                    name=p.name,
                    description=p.description,
                    start_date=p.start_date,
                    end_date=p.end_date,
                    status=p.status,
                    budget=float(p.budget) if p.budget else None,
                )
                for p in projects
            ]
    
    @strawberry.field
    async def dashboard_stats(self, info: strawberry.Info) -> DashboardStats:
        """Получение статистики для дашборда"""
        from app.core.database import async_session_maker
        from app.models.employee import Employee as EmployeeModel
        from app.models.project import Project as ProjectModel
        from app.models.task import Task as TaskModel
        from sqlalchemy import select, func
        
        async with async_session_maker() as session:
            # Employees
            employees_total = await session.scalar(select(func.count(EmployeeModel.employee_id)))
            employees_active = await session.scalar(
                select(func.count(EmployeeModel.employee_id)).where(
                    EmployeeModel.termination_date.is_(None)
                )
            )
            
            # Projects
            projects_total = await session.scalar(select(func.count(ProjectModel.project_id)))
            projects_active = await session.scalar(
                select(func.count(ProjectModel.project_id)).where(ProjectModel.status == 'active')
            )
            
            # Tasks (заглушка, нужно импортировать TaskModel)
            tasks_total = 0
            tasks_pending = 0
            
            return DashboardStats(
                employees_total=employees_total or 0,
                employees_active=employees_active or 0,
                projects_total=projects_total or 0,
                projects_active=projects_active or 0,
                tasks_total=tasks_total,
                tasks_pending=tasks_pending,
                assets_total=0,
            )


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_employee(
        self,
        info: strawberry.Info,
        full_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        hire_date: datetime = None,
        department_id: int = 0,
        position_id: int = 0,
    ) -> Employee:
        """Создание сотрудника"""
        from app.core.database import async_session_maker
        from app.models.employee import Employee as EmployeeModel
        
        async with async_session_maker() as session:
            employee = EmployeeModel(
                full_name=full_name,
                email=email,
                phone=phone,
                hire_date=hire_date or datetime.now().date(),
                department_id=department_id,
                position_id=position_id,
            )
            
            session.add(employee)
            await session.commit()
            await session.refresh(employee)
            
            return Employee(
                employee_id=employee.employee_id,
                full_name=employee.full_name,
                email=employee.email,
                phone=employee.phone,
                hire_date=employee.hire_date,
                department_id=employee.department_id,
                position_id=employee.position_id,
                manager_id=employee.manager_id,
                personnel_number=employee.personnel_number,
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)
