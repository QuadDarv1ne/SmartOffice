from datetime import date, datetime
from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Text, Numeric as SQLNumeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendance"
    
    attendance_id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"))
    work_date: Mapped[date] = mapped_column(Date)
    check_in: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    check_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hours_worked: Mapped[float | None] = mapped_column(SQLNumeric(4, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="present")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    employee: Mapped["Employee"] = relationship("Employee")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    request_id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    leave_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("employees.employee_id"), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    approver: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[approved_by])
