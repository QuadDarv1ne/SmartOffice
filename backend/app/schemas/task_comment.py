"""
Task Comment схемы
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Текст комментария")


class TaskCommentCreate(TaskCommentBase):
    parent_id: Optional[int] = Field(None, ge=1, description="ID родительского комментария")


class TaskCommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class TaskCommentResponse(TaskCommentBase):
    id: int
    task_id: int
    author_id: int
    parent_id: Optional[int] = None
    is_edited: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Дополнительные поля (заполняются при необходимости)
    author_email: Optional[str] = None
    author_name: Optional[str] = None
    replies_count: int = 0
    
    class Config:
        from_attributes = True


class TaskCommentListResponse(BaseModel):
    total: int
    comments: list[TaskCommentResponse]
