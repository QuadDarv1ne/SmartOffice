"""
Audit Log API для просмотра журнала аудита
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.services.audit_log_service import AuditLogService, create_audit_log_service

router = APIRouter(prefix="/audit", tags=["Audit Log"])


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditLogService:
    """Factory для получения AuditLogService"""
    return create_audit_log_service(db)


@router.get("/logs")
async def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: AuditLogService = Depends(get_audit_service),
    current_user: User = Depends(get_current_admin),
):
    """
    Получение записей audit log
    
    Доступно только администраторам
    """
    logs, total = await service.get_logs(
        user_id=user_id,
        entity_type=entity_type,
        action=action,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "ip_address": log.ip_address,
                "status": log.status,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
    }


@router.get("/logs/stats")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    service: AuditLogService = Depends(get_audit_service),
    current_user: User = Depends(get_current_admin),
):
    """
    Статистика audit log за период
    
    Доступно только администраторам
    """
    from datetime import timedelta
    from sqlalchemy import select, func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Статистика по действиям
    action_query = select(
        AuditLog.action,
        func.count(AuditLog.id).label('count'),
    ).where(AuditLog.created_at >= start_date).group_by(AuditLog.action)
    
    result = await service.db.execute(action_query)
    by_action = {row[0]: row[1] for row in result.all()}
    
    # Статистика по сущностям
    entity_query = select(
        AuditLog.entity_type,
        func.count(AuditLog.id).label('count'),
    ).where(AuditLog.created_at >= start_date).group_by(AuditLog.entity_type)
    
    result = await service.db.execute(entity_query)
    by_entity = {row[0]: row[1] for row in result.all()}
    
    # Неуспешные операции
    failures_query = select(
        func.count(AuditLog.id)
    ).where(
        AuditLog.created_at >= start_date,
        AuditLog.status == 'failure',
    )
    failures = await service.db.scalar(failures_query)
    
    return {
        "period_days": days,
        "by_action": by_action,
        "by_entity": by_entity,
        "total": sum(by_action.values()),
        "failures": failures,
        "failure_rate": round(failures / sum(by_action.values()) * 100, 2) if by_action else 0,
    }


# Импорт для статистики
from app.models.audit_log import AuditLog
