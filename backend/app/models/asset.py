from datetime import date, datetime
from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"
    
    asset_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(50))
    serial_number: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    supplier_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="available")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    assignments: Mapped[list["AssetAssignment"]] = relationship("AssetAssignment", back_populates="asset", cascade="all, delete-orphan")


class AssetAssignment(Base):
    __tablename__ = "asset_assignments"
    
    assignment_id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.asset_id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"))
    assigned_date: Mapped[date] = mapped_column(Date, default=date.today)
    returned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    condition_on_return: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    asset: Mapped["Asset"] = relationship("Asset", back_populates="assignments")
    employee: Mapped["Employee"] = relationship("Employee")
