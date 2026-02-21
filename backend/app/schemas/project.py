from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "active"
    manager_id: Optional[int] = None
    budget: Optional[float] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    actual_cost: Optional[float] = None


class ProjectResponse(ProjectBase):
    project_id: int
    actual_cost: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    deadline: Optional[date] = None
    priority: str = "medium"
    estimated_hours: Optional[float] = None
    status: str = "new"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    deadline: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    estimated_hours: Optional[float] = None


class TaskResponse(TaskBase):
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectTeamCreate(BaseModel):
    employee_id: int
    role: Optional[str] = None


class ProjectTeamResponse(BaseModel):
    project_id: int
    employee_id: int
    role: Optional[str] = None
    joined_date: date

    class Config:
        from_attributes = True
