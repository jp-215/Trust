"""Schemas for the /health route."""

from pydantic import BaseModel


class DependencyStatus(BaseModel):
    """Configuration status of each downstream dependency."""

    databricks_configured: bool
    gemini_configured: bool


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dependencies: DependencyStatus
