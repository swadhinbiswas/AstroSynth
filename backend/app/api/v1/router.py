from fastapi import APIRouter

from app.api.v1.endpoints import auth, catalog, feedback, health, predict

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(catalog.router)
router.include_router(predict.router)
router.include_router(feedback.router)
router.include_router(auth.router)
