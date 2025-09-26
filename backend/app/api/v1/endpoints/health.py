from fastapi import APIRouter

from app import __version__
from app.schemas import HealthResponse
from app.services.predictor import get_model

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    try:
        get_model()
        loaded = True
    except Exception:
        loaded = False
    return HealthResponse(status="ok", version=__version__, model_loaded=loaded)


@router.get("/ready")
def ready():
    return {"ready": True}


@router.get("/live")
def live():
    return {"live": True}
