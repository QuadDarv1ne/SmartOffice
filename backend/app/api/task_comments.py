"""
Task Comments API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentUpdate,
    TaskCommentResponse,
    TaskCommentListResponse,
)
from app.services.task_comment_service import TaskCommentService, create_task_comment_service

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["Task Comments"])


def get_comment_service(db: AsyncSession = Depends(get_db)) -> TaskCommentService:
    """Factory для получения TaskCommentService"""
    return create_task_comment_service(db)


@router.get("/", response_model=TaskCommentListResponse)
async def get_task_comments(
    task_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: TaskCommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
):
    """Получение комментариев к задаче"""
    comments, total = await service.get_comments(task_id, limit, offset)
    
    # enrich с данными авторов
    enriched_comments = []
    for comment in comments:
        enriched = {
            "id": comment.id,
            "task_id": comment.task_id,
            "author_id": comment.author_id,
            "parent_id": comment.parent_id,
            "content": comment.content,
            "is_edited": comment.is_edited,
            "is_deleted": comment.is_deleted,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "author_email": getattr(comment, 'author_email', None),
            "author_name": getattr(comment, 'author_name', None),
        }
        enriched_comments.append(enriched)
    
    return {
        "total": total,
        "comments": enriched_comments,
    }


@router.post("/", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_task_comment(
    task_id: int,
    comment_data: TaskCommentCreate,
    service: TaskCommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
):
    """Создание комментария к задаче"""
    try:
        comment = await service.create_comment(
            task_id=task_id,
            author_id=current_user.id,
            comment_data=comment_data,
        )
        
        return TaskCommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            parent_id=comment.parent_id,
            content=comment.content,
            is_edited=comment.is_edited,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{comment_id}", response_model=TaskCommentResponse)
async def update_task_comment(
    task_id: int,
    comment_id: int,
    comment_data: TaskCommentUpdate,
    service: TaskCommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
):
    """Обновление комментария (только автор)"""
    comment = await service.update_comment(
        comment_id=comment_id,
        author_id=current_user.id,
        comment_data=comment_data,
    )
    
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found or you don't have permission",
        )
    
    return TaskCommentResponse(
        id=comment.id,
        task_id=comment.task_id,
        author_id=comment.author_id,
        parent_id=comment.parent_id,
        content=comment.content,
        is_edited=comment.is_edited,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_comment(
    task_id: int,
    comment_id: int,
    service: TaskCommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
):
    """Удаление комментария"""
    success = await service.delete_comment(
        comment_id=comment_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Comment not found or you don't have permission",
        )
