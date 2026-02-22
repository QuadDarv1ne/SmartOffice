"""
WebSocket менеджер подключений

Управляет активными WebSocket подключениями и рассылкой уведомлений
"""

from typing import Dict, List, Set
from fastapi import WebSocket
import structlog
import json

logger = structlog.get_logger("smartoffice")


class ConnectionManager:
    """Менеджер WebSocket подключений"""
    
    def __init__(self):
        # Активные подключения по user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Подключения по комнатам (projects, departments, etc.)
        self.rooms: Dict[str, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """Подключение клиента"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        logger.info(
            "WebSocket client connected",
            user_id=user_id,
            total_connections=len(self.active_connections),
        )
    
    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        """Отключение клиента"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(
            "WebSocket client disconnected",
            user_id=user_id,
        )
    
    async def send_personal_message(self, message: dict, user_id: int) -> None:
        """Отправка сообщения конкретному пользователю"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(
                        "Failed to send message",
                        user_id=user_id,
                        error=str(e),
                    )
    
    async def broadcast(self, message: dict) -> None:
        """Рассылка сообщения всем подключенным клиентам"""
        disconnected = []
        
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append((user_id, connection))
        
        # Удаляем отключившихся клиентов
        for user_id, connection in disconnected:
            self.disconnect(connection, user_id)
    
    async def broadcast_to_room(self, room: str, message: dict) -> None:
        """Рассылка сообщения комнате"""
        if room not in self.rooms:
            return
        
        for user_id in self.rooms[room]:
            await self.send_personal_message(message, user_id)
    
    def join_room(self, user_id: int, room: str) -> None:
        """Присоединение к комнате"""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(user_id)
        
        logger.debug("User joined room", user_id=user_id, room=room)
    
    def leave_room(self, user_id: int, room: str) -> None:
        """Покидание комнаты"""
        if room in self.rooms:
            self.rooms[room].discard(user_id)
        
        logger.debug("User left room", user_id=user_id, room=room)
    
    def get_stats(self) -> dict:
        """Получение статистики подключений"""
        return {
            "total_users": len(self.active_connections),
            "total_connections": sum(len(conns) for conns in self.active_connections.values()),
            "rooms": {room: len(users) for room, users in self.rooms.items()},
        }


# Глобальный менеджер
manager = ConnectionManager()


# Типы уведомлений
class NotificationType:
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_ASSIGNED = "task_assigned"
    PROJECT_UPDATED = "project_updated"
    EMPLOYEE_ADDED = "employee_added"
    EMPLOYEE_UPDATED = "employee_updated"
    MESSAGE_RECEIVED = "message_received"
    SYSTEM = "system"


def create_notification(
    notification_type: str,
    title: str,
    message: str,
    data: dict = None,
) -> dict:
    """Создание уведомления"""
    return {
        "type": "notification",
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "data": data or {},
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
