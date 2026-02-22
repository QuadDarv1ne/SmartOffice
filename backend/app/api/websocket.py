"""
WebSocket API для real-time уведомлений
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.websocket import manager, create_notification, NotificationType
from app.api.deps import get_current_user
from app.models.user import User

logger = structlog.get_logger("smartoffice")

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    token: str = Query(...),
):
    """
    WebSocket endpoint для получения уведомлений
    
    Подключение: ws://localhost:8000/api/ws/notifications?token=<access_token>
    """
    # Получаем пользователя из токена
    # (в реальном приложении нужна валидация токена)
    from app.core.security import verify_access_token
    
    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    user_id = int(payload.get("sub", 0))
    if not user_id:
        await websocket.close(code=4001, reason="Invalid user")
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Получаем данные от клиента (например, подписка на комнаты)
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "join_room":
                room = data.get("room")
                if room:
                    manager.join_room(user_id, room)
                    await websocket.send_json({
                        "type": "system",
                        "message": f"Joined room: {room}",
                    })
            
            elif action == "leave_room":
                room = data.get("room")
                if room:
                    manager.leave_room(user_id, room)
            
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info("WebSocket disconnected", user_id=user_id)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        manager.disconnect(websocket, user_id)


@router.get("/notifications/stats")
async def get_notification_stats(current_user: User = Depends(get_current_user)):
    """Получение статистики WebSocket подключений"""
    return manager.get_stats()


# Helper функции для отправки уведомлений
async def notify_task_created(task_id: int, project_id: int, assigned_to: int = None):
    """Уведомление о создании задачи"""
    notification = create_notification(
        NotificationType.TASK_CREATED,
        "Новая задача",
        f"Создана новая задача #{task_id}",
        {"task_id": task_id, "project_id": project_id},
    )
    
    # Отправляем назначенному пользователю
    if assigned_to:
        await manager.send_personal_message(notification, assigned_to)
    
    # Отправляем в комнату проекта
    await manager.broadcast_to_room(f"project:{project_id}", notification)


async def notify_task_assigned(task_id: int, assigned_to: int, assigned_by: int):
    """Уведомление о назначении задачи"""
    notification = create_notification(
        NotificationType.TASK_ASSIGNED,
        "Вам назначена задача",
        f"Вам назначена задача #{task_id}",
        {"task_id": task_id, "assigned_by": assigned_by},
    )
    await manager.send_personal_message(notification, assigned_to)


async def notify_employee_added(employee_id: int, full_name: str):
    """Уведомление о добавлении сотрудника"""
    notification = create_notification(
        NotificationType.EMPLOYEE_ADDED,
        "Новый сотрудник",
        f"Добавлен сотрудник: {full_name}",
        {"employee_id": employee_id},
    )
    await manager.broadcast(notification)


async def notify_project_updated(project_id: int, update_type: str):
    """Уведомление об обновлении проекта"""
    notification = create_notification(
        NotificationType.PROJECT_UPDATED,
        "Обновление проекта",
        f"Проект #{project_id} был обновлен",
        {"project_id": project_id, "update_type": update_type},
    )
    await manager.broadcast_to_room(f"project:{project_id}", notification)
