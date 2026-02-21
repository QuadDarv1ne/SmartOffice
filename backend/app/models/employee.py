from datetime import date, datetime
from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"
    
    department_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    manager_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")


class Position(Base):
    __tablename__ = "positions"
    
    position_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    min_salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)


class Employee(Base):
    __tablename__ = "employees"
    
    employee_id: Mapped[int] = mapped_column(primary_key=True)
    personnel_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(150))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    hire_date: Mapped[date] = mapped_column(Date)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.department_id"))
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.position_id"))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.employee_id"), nullable=True)
    schedule_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    department: Mapped["Department"] = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    position: Mapped["Position"] = relationship("Position")
    manager: Mapped["Employee | None"] = relationship("Employee", remote_side=[employee_id], foreign_keys=[manager_id])
