from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class DepartmentBase(BaseModel):
    name: str
    manager_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    department_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    title: str
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None


class PositionCreate(PositionBase):
    pass


class PositionResponse(PositionBase):
    position_id: int

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hire_date: date
    department_id: int
    position_id: int
    manager_id: Optional[int] = None
    schedule_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    manager_id: Optional[int] = None
    termination_date: Optional[date] = None


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
