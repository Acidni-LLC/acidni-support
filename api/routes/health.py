"""
Health check endpoint.

Standard /health endpoint for Container App probes and APIM health checks.
"""

from fastapi import APIRouter

from api.config import get_settings
from api.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check — returns service status, version, and environment."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        service="acidni-support",
    )
