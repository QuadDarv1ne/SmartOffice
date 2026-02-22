"""
Metrics API endpoint для Prometheus
"""

from fastapi import APIRouter, Response
from app.core.metrics import generate_metrics, metrics_content_type

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint
    
    Используйте с Prometheus scraper:
    
    scrape_configs:
      - job_name: 'smartoffice'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/api/metrics'
    """
    return Response(
        content=generate_metrics(),
        media_type=metrics_content_type(),
    )
