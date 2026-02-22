"""
Middleware для сбора Prometheus метрик
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import structlog

from app.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
)

logger = structlog.get_logger("smartoffice")


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware для сбора метрик запросов"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Игнорируем метрики для /metrics endpoint
        if request.url.path == '/metrics':
            return await call_next(request)
        
        method = request.method
        endpoint = self._get_endpoint_path(request.url.path)
        
        # Увеличиваем счётчик запросов в обработке
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Записываем метрики успешного запроса
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Записываем метрики ошибки
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            logger.error(
                "Request error",
                method=method,
                endpoint=endpoint,
                duration=duration,
                error=str(e),
            )
            raise
            
        finally:
            # Уменьшаем счётчик запросов в обработке
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
    
    def _get_endpoint_path(self, path: str) -> str:
        """Нормализация пути endpoint'а для метрик"""
        # Заменяем ID на плейсхолдеры
        import re
        normalized = re.sub(r'/\d+', '/{id}', path)
        normalized = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', normalized)
        return normalized
