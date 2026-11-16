"""Route: /health"""

from fastapi import APIRouter

from handlers import health_handler
from models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Standard health check with dependency configuration status."""
    return await health_handler.get_health()
