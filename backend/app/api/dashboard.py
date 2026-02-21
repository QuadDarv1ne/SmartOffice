from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.employee import Employee, Department
from app.models.project import Project, Task
from app.models.asset import Asset
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Employee stats
    total_employees = await db.scalar(select(func.count(Employee.employee_id)))
    active_employees = await db.scalar(
        select(func.count(Employee.employee_id)).where(Employee.termination_date == None)
    )
    
    # Department stats
    total_departments = await db.scalar(select(func.count(Department.department_id)))
    
    # Project stats
    total_projects = await db.scalar(select(func.count(Project.project_id)))
    active_projects = await db.scalar(
        select(func.count(Project.project_id)).where(Project.status == "active")
    )
    
    # Task stats
    total_tasks = await db.scalar(select(func.count(Task.task_id)))
    pending_tasks = await db.scalar(
        select(func.count(Task.task_id)).where(Task.status.in_(["new", "in_progress"]))
    )
    completed_tasks = await db.scalar(
        select(func.count(Task.task_id)).where(Task.status == "completed")
    )
    
    # Asset stats
    total_assets = await db.scalar(select(func.count(Asset.asset_id)))
    available_assets = await db.scalar(
        select(func.count(Asset.asset_id)).where(Asset.status == "available")
    )
    in_use_assets = await db.scalar(
        select(func.count(Asset.asset_id)).where(Asset.status == "in_use")
    )
    
    return {
        "employees": {
            "total": total_employees or 0,
            "active": active_employees or 0,
        },
        "departments": total_departments or 0,
        "projects": {
            "total": total_projects or 0,
            "active": active_projects or 0,
        },
        "tasks": {
            "total": total_tasks or 0,
            "pending": pending_tasks or 0,
            "completed": completed_tasks or 0,
        },
        "assets": {
            "total": total_assets or 0,
            "available": available_assets or 0,
            "in_use": in_use_assets or 0,
        }
    }


@router.get("/employees-by-department")
async def get_employees_by_department(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(
            Department.name,
            func.count(Employee.employee_id).label("count")
        )
        .join(Employee, Department.department_id == Employee.department_id)
        .where(Employee.termination_date == None)
        .group_by(Department.department_id, Department.name)
        .order_by(func.count(Employee.employee_id).desc())
    )
    
    return [
        {"department": row.name, "count": row.count}
        for row in result.all()
    ]


@router.get("/tasks-by-status")
async def get_tasks_by_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(
            Task.status,
            func.count(Task.task_id).label("count")
        )
        .group_by(Task.status)
        .order_by(func.count(Task.task_id).desc())
    )
    
    return [
        {"status": row.status, "count": row.count}
        for row in result.all()
    ]


@router.get("/projects-by-status")
async def get_projects_by_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(
            Project.status,
            func.count(Project.project_id).label("count")
        )
        .group_by(Project.status)
        .order_by(func.count(Project.project_id).desc())
    )
    
    return [
        {"status": row.status, "count": row.count}
        for row in result.all()
    ]
