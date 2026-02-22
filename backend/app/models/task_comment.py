"""
Task Comments модель для комментариев к задачам
"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TaskComment(Base):
    __tablename__ = "task_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Связь с задачей
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Автор комментария
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Родительский комментарий (для вложенности)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("task_comments.id"), nullable=True, index=True)
    
    # Содержание
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Статус
    is_edited: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    # task = relationship("Task", back_populates="comments")
    # author = relationship("User", back_populates="task_comments")
    # parent = relationship("TaskComment", remote_side=[id], back_populates="replies")
    # replies = relationship("TaskComment", back_populates="parent")

    def __repr__(self):
        return f"<TaskComment {self.id} - Task {self.task_id} by {self.author_id}>"
