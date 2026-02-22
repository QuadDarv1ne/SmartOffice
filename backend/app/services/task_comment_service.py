"""
Task Comments Service
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
import structlog

from app.models.task_comment import TaskComment
from app.models.task import Task
from app.models.user import User
from app.schemas.task_comment import TaskCommentCreate, TaskCommentUpdate
from app.core.websocket import manager, create_notification, NotificationType

logger = structlog.get_logger("smartoffice")


class TaskCommentService:
    """Сервис для управления комментариями к задачам"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_comments(
        self,
        task_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[TaskComment], int]:
        """Получение комментариев к задаче"""
        
        # Общее количество
        count_query = select(func.count()).select_from(
            select(TaskComment).where(TaskComment.task_id == task_id).subquery()
        )
        total = await self.db.scalar(count_query)
        
        # Комментарии с данными авторов
        query = (
            select(TaskComment)
            .options(selectinload(TaskComment.author))
            .where(TaskComment.task_id == task_id)
            .where(TaskComment.is_deleted == False)
            .order_by(TaskComment.created_at)
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        comments = result.scalars().all()
        
        return list(comments), total
    
    async def create_comment(
        self,
        task_id: int,
        author_id: int,
        comment_data: TaskCommentCreate,
    ) -> TaskComment:
        """Создание комментария"""
        
        # Проверяем существование задачи
        task = await self.db.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        
        comment = TaskComment(
            task_id=task_id,
            author_id=author_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
        )
        
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        
        # Отправляем уведомление
        await self._notify_comment_created(comment, task)
        
        logger.info(
            "Task comment created",
            comment_id=comment.id,
            task_id=task_id,
            author_id=author_id,
        )
        
        return comment
    
    async def update_comment(
        self,
        comment_id: int,
        author_id: int,
        comment_data: TaskCommentUpdate,
    ) -> Optional[TaskComment]:
        """Обновление комментария (только автор может редактировать)"""
        
        comment = await self.db.get(TaskComment, comment_id)
        if not comment or comment.author_id != author_id:
            return None
        
        comment.content = comment_data.content
        comment.is_edited = True
        
        await self.db.commit()
        await self.db.refresh(comment)
        
        logger.info(
            "Task comment updated",
            comment_id=comment_id,
            author_id=author_id,
        )
        
        return comment
    
    async def delete_comment(
        self,
        comment_id: int,
        user_id: int,
        hard_delete: bool = False,
    ) -> bool:
        """
        Удаление комментария
        
        Args:
            hard_delete: Полное удаление (только для админов)
        """
        
        comment = await self.db.get(TaskComment, comment_id)
        if not comment:
            return False
        
        # Проверяем права (автор или админ)
        if comment.author_id != user_id:
            # Здесь можно проверить is_admin
            return False
        
        if hard_delete:
            await self.db.delete(comment)
        else:
            # Мягкое удаление
            comment.is_deleted = True
            comment.content = "[Удалено]"
        
        await self.db.commit()
        
        logger.info(
            "Task comment deleted",
            comment_id=comment_id,
            hard_delete=hard_delete,
        )
        
        return True
    
    async def get_comment(self, comment_id: int) -> Optional[TaskComment]:
        """Получение одного комментария"""
        return await self.db.get(TaskComment, comment_id)
    
    async def _notify_comment_created(self, comment: TaskComment, task: Task):
        """Отправка уведомления о новом комментарии"""
        
        notification = create_notification(
            NotificationType.TASK_ASSIGNED,  # Можно создать новый тип
            "Новый комментарий",
            f"Добавлен комментарий к задаче #{task_id}",
            {
                "task_id": task.task_id,
                "task_title": task.title,
                "comment_id": comment.id,
            },
        )
        
        # Отправляем назначенному пользователю
        if task.assigned_to:
            await manager.send_personal_message(notification, task.assigned_to)


def create_task_comment_service(db: AsyncSession) -> TaskCommentService:
    """Factory для создания сервиса"""
    return TaskCommentService(db)
