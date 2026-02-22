from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse
)
from app.api.deps import get_current_user
from app.services.employee_service import EmployeeService
from app.models.user import User

router = APIRouter(prefix="/employees", tags=["Employees"])


def get_employee_service(db: AsyncSession = Depends(get_db)) -> EmployeeService:
    """Factory для получения EmployeeService"""
    return EmployeeService(db)


@router.get("/", response_model=dict)
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department_id: Optional[int] = None,
    search: Optional[str] = None,
    service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user),
):
    """Получение списка сотрудников с пагинацией"""
    try:
        employees, total = await service.get_employees(
            skip=skip,
            limit=limit,
            department_id=department_id,
            search=search,
        )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": employees,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user),
):
    """Получение сотрудника по ID"""
    employee = await service.get_employee_by_id(employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user),
):
    """Создание нового сотрудника"""
    try:
        employee = await service.create_employee(employee_data)
        return employee
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user),
):
    """Обновление данных сотрудника"""
    try:
        employee = await service.update_employee(employee_id, employee_data)

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user),
):
    """Удаление сотрудника"""
    success = await service.delete_employee(employee_id)

    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
