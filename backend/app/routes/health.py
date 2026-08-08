from fastapi import APIRouter

from app.config import settings
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        version=settings.app_version,
    )
