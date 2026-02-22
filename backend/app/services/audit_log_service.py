"""
Audit Log Service для журналирования действий пользователей
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
import structlog

from app.models.audit_log import AuditLog

logger = structlog.get_logger("smartoffice")


class AuditLogService:
    """Сервис для работы с audit log"""
    
    # Типы действий
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_VIEW = "VIEW"
    ACTION_EXPORT = "EXPORT"
    ACTION_UPLOAD = "UPLOAD"
    ACTION_DOWNLOAD = "DOWNLOAD"
    ACTION_PASSWORD_CHANGE = "PASSWORD_CHANGE"
    ACTION_2FA_ENABLE = "2FA_ENABLE"
    ACTION_2FA_DISABLE = "2FA_DISABLE"
    
    # Сущности
    ENTITY_USER = "User"
    ENTITY_EMPLOYEE = "Employee"
    ENTITY_DEPARTMENT = "Department"
    ENTITY_POSITION = "Position"
    ENTITY_PROJECT = "Project"
    ENTITY_TASK = "Task"
    ENTITY_ASSET = "Asset"
    ENTITY_FILE = "File"
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log(
        self,
        action: str,
        entity_type: str,
        user_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
    ) -> AuditLog:
        """
        Создание записи в audit log
        
        Args:
            action: Тип действия (LOGIN, CREATE, UPDATE, DELETE, etc.)
            entity_type: Тип сущности (User, Employee, Project, etc.)
            user_id: ID пользователя
            entity_id: ID сущности
            description: Описание действия
            old_values: Старые значения (для UPDATE/DELETE)
            new_values: Новые значения (для CREATE/UPDATE)
            ip_address: IP адрес
            user_agent: User agent
            status: Статус (success, failure)
        
        Returns:
            Созданная запись AuditLog
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )
        
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        
        logger.debug(
            "Audit log created",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            status=status,
        )
        
        return audit_log
    
    async def login(
        self,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
    ):
        """Логирование входа пользователя"""
        return await self.log(
            action=self.ACTION_LOGIN,
            entity_type=self.ENTITY_USER,
            entity_id=user_id,
            user_id=user_id,
            description=f"User login {'successful' if status == 'success' else 'failed'}",
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )
    
    async def logout(
        self,
        user_id: int,
        ip_address: Optional[str] = None,
    ):
        """Логирование выхода пользователя"""
        return await self.log(
            action=self.ACTION_LOGOUT,
            entity_type=self.ENTITY_USER,
            entity_id=user_id,
            user_id=user_id,
            description="User logout",
            ip_address=ip_address,
        )
    
    async def create(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        new_values: Dict[str, Any],
        ip_address: Optional[str] = None,
    ):
        """Логирование создания сущности"""
        return await self.log(
            action=self.ACTION_CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            description=f"Created {entity_type} #{entity_id}",
            new_values=new_values,
            ip_address=ip_address,
        )
    
    async def update(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        ip_address: Optional[str] = None,
    ):
        """Логирование обновления сущности"""
        return await self.log(
            action=self.ACTION_UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            description=f"Updated {entity_type} #{entity_id}",
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
    
    async def delete(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        ip_address: Optional[str] = None,
    ):
        """Логирование удаления сущности"""
        return await self.log(
            action=self.ACTION_DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            description=f"Deleted {entity_type} #{entity_id}",
            old_values=old_values,
            ip_address=ip_address,
        )
    
    async def get_logs(
        self,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        """
        Получение записей audit log с фильтрацией
        
        Returns:
            (список записей, общее количество)
        """
        query = select(AuditLog)
        
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        
        if action:
            query = query.where(AuditLog.action == action)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        
        # Общее количество
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        # Получаем записи
        query = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total


def create_audit_log_service(db: AsyncSession) -> AuditLogService:
    """Factory для создания сервиса"""
    return AuditLogService(db)
