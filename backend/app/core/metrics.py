"""
Prometheus метрики для мониторинга приложения
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
import time
import psutil
from typing import Optional
import structlog

logger = structlog.get_logger("smartoffice")

# ============================================
# Метрики запросов
# ============================================

# Количество HTTP запросов
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Время обработки запросов
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Количество запросов в обработке
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

# ============================================
# Метрики базы данных
# ============================================

db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['status']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# ============================================
# Метрики системы
# ============================================

system_cpu_percent = Gauge(
    'system_cpu_percent',
    'System CPU usage percent'
)

system_memory_percent = Gauge(
    'system_memory_percent',
    'System memory usage percent'
)

system_disk_percent = Gauge(
    'system_disk_percent',
    'System disk usage percent'
)

# ============================================
# Метрики бизнес-логики
# ============================================

employees_total = Gauge(
    'employees_total',
    'Total number of employees'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

tasks_created_total = Counter(
    'tasks_created_total',
    'Total tasks created'
)

projects_active = Gauge(
    'projects_active',
    'Number of active projects'
)

# ============================================
# Метрики WebSocket
# ============================================

websocket_connections = Gauge(
    'websocket_connections',
    'Number of active WebSocket connections'
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['type']
)


def update_system_metrics():
    """Обновление системных метрик"""
    try:
        system_cpu_percent.set(psutil.cpu_percent(interval=1))
        system_memory_percent.set(psutil.virtual_memory().percent)
        system_disk_percent.set(psutil.disk_usage('/').percent)
    except Exception as e:
        logger.warning("Failed to update system metrics", error=str(e))


def generate_metrics() -> str:
    """Генерация всех метрик в формате Prometheus"""
    update_system_metrics()
    return generate_latest().decode('utf-8')


def metrics_content_type() -> str:
    """Content-Type для Prometheus метрик"""
    return CONTENT_TYPE_LATEST
