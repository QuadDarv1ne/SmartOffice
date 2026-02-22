from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название отдела")
    manager_id: Optional[int] = Field(None, ge=1, description="ID менеджера отдела")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    department_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Название должности")
    min_salary: Optional[float] = Field(None, ge=0, description="Минимальная зарплата")
    max_salary: Optional[float] = Field(None, ge=0, description="Максимальная зарплата")
    
    class Config:
        validate_assignment = True


class PositionCreate(PositionBase):
    pass


class PositionResponse(PositionBase):
    position_id: int

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150, description="ФИО сотрудника")
    email: Optional[EmailStr] = Field(None, description="Email")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    hire_date: date = Field(..., description="Дата приёма на работу")
    department_id: int = Field(..., ge=1, description="ID отдела")
    position_id: int = Field(..., ge=1, description="ID должности")
    manager_id: Optional[int] = Field(None, ge=1, description="ID непосредственного руководителя")
    schedule_id: Optional[int] = Field(None, ge=1, description="ID графика работы")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = Field(None, ge=1)
    position_id: Optional[int] = Field(None, ge=1)
    manager_id: Optional[int] = Field(None, ge=1)
    termination_date: Optional[date] = None
    
    class Config:
        validate_assignment = True


class EmployeeResponse(EmployeeBase):
    employee_id: int
    personnel_number: Optional[str] = None
    birth_date: Optional[date] = None
    termination_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    employee_id: int
    full_name: str
    email: Optional[str] = None
    department_id: int
    position_id: int
    hire_date: date

    class Config:
        from_attributes = True
