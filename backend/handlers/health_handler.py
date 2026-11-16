"""Business logic for the /health route."""

from core.config import settings
from models.health import DependencyStatus, HealthResponse


async def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        dependencies=DependencyStatus(
            databricks_configured=settings.databricks_configured,
            gemini_configured=settings.gemini_configured,
        ),
    )
