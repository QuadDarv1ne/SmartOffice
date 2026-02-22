"""
Audit Log модель для журналирования всех действий в системе
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Кто совершил действие
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    # Тип действия
    action: Mapped[str] = mapped_column(String(50), index=True)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    
    # Над какой сущностью действие
    entity_type: Mapped[str] = mapped_column(String(50), index=True)  # User, Employee, Project, Task, etc.
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Детали действия
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Старые и новые значения (JSON)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Метаданные
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Статус
    status: Mapped[str] = mapped_column(String(20), default="success")  # success, failure
    
    # Время
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Связь с пользователем
    # user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.id} - {self.action} on {self.entity_type} by user {self.user_id}>"
