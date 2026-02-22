"""
Health checks для мониторинга состояния системы
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import structlog

from app.core.database import get_db
from app.core.websocket import manager
from app.models.user import User
from app.models.employee import Employee

logger = structlog.get_logger("smartoffice")

router = APIRouter(tags=["Health Checks"])


async def check_database(db: AsyncSession) -> Dict[str, Any]:
    """Проверка подключения к базе данных"""
    start_time = time.time()
    
    try:
        # Простой запрос
        await db.execute(select(1))
        
        # Проверка количества таблиц
        result = await db.execute(
            text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
        )
        tables_count = result.scalar()
        
        # Количество записей в основных таблицах
        users_count = await db.scalar(select(func.count()).select_from(User))
        employees_count = await db.scalar(select(func.count()).select_from(Employee))
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "tables_count": tables_count,
            "users_count": users_count,
            "employees_count": employees_count,
        }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def check_websocket() -> Dict[str, Any]:
    """Проверка WebSocket подключений"""
    try:
        stats = manager.get_stats()
        return {
            "status": "healthy",
            "connections": stats,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def check_memory() -> Dict[str, Any]:
    """Проверка использования памяти"""
    import psutil
    process = psutil.Process()
    
    memory_info = process.memory_info()
    
    return {
        "status": "healthy",
        "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
        "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
        "percent": round(process.memory_percent(), 2),
    }


async def check_disk() -> Dict[str, Any]:
    """Проверка дискового пространства"""
    import psutil
    
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy" if disk.percent < 90 else "warning",
        "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
        "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
        "percent": disk.percent,
    }


@router.get("/health")
async def health_check():
    """
    Basic health check
    
    Возвращает простой статус healthy/unhealthy
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe
    
    Проверяет, готово ли приложение принимать запросы
    """
    db_status = await check_database(db)
    
    is_ready = db_status["status"] == "healthy"
    
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": {
                "database": db_status,
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe
    
    Проверяет, что приложение не зависло
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/full")
async def full_health_check(db: AsyncSession = Depends(get_db)):
    """
    Полный health check всех компонентов
    
    Возвращает детальную информацию о состоянии системы
    """
    start_time = time.time()
    
    # Запускаем проверки параллельно
    db_status, ws_status, memory_status, disk_status = await asyncio.gather(
        check_database(db),
        check_websocket(),
        check_memory(),
        check_disk(),
        return_exceptions=True,
    )
    
    # Обработка исключений
    for name, status in [("database", db_status), ("websocket", ws_status), 
                          ("memory", memory_status), ("disk", disk_status)]:
        if isinstance(status, Exception):
            logger.error(f"{name} health check failed", error=str(status))
    
    total_time = (time.time() - start_time) * 1000
    
    # Определяем общий статус
    statuses = [
        db_status.get("status") if isinstance(db_status, dict) else "unhealthy",
        ws_status.get("status") if isinstance(ws_status, dict) else "unhealthy",
        memory_status.get("status") if isinstance(memory_status, dict) else "unhealthy",
        disk_status.get("status") if isinstance(disk_status, dict) else "unhealthy",
    ]
    
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif "warning" in statuses:
        overall_status = "degraded"
        status_code = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        status_code = status.HTTP_200_OK
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "checks": {
                "database": db_status if isinstance(db_status, dict) else {"error": str(db_status)},
                "websocket": ws_status if isinstance(ws_status, dict) else {"error": str(ws_status)},
                "memory": memory_status if isinstance(memory_status, dict) else {"error": str(memory_status)},
                "disk": disk_status if isinstance(disk_status, dict) else {"error": str(disk_status)},
            },
            "total_time_ms": round(total_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Импорт func для запросов
from sqlalchemy import func
