from fastapi import APIRouter

from app.agent.llm_provider import get_active_model_name
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def check_health():
    """Simple check to know the app is running and which model it really uses."""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "provider": settings.llm_provider,
        "model": get_active_model_name(),
    }
