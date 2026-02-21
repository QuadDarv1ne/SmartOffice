from datetime import date, datetime
from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    
    project_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    manager_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    actual_cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    team: Mapped[list["ProjectTeam"]] = relationship("ProjectTeam", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"
    
    task_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("employees.employee_id"), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    estimated_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[assigned_to])


class ProjectTeam(Base):
    __tablename__ = "project_team"
    
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), primary_key=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    joined_date: Mapped[date] = mapped_column(Date, default=date.today)
    
    project: Mapped["Project"] = relationship("Project", back_populates="team")
    employee: Mapped["Employee"] = relationship("Employee")
