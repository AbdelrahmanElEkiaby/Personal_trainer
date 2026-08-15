from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def check_health():
    """Simple check to know the app is running and which model it uses."""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "model": settings.ollama_model,
    }
