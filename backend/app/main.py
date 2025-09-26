"""AstroSynth FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.responses import Response

from app import __version__
from app.api.v1.router import router
from app.core.config import get_settings
from app.core.logging import configure_logging, logger
from app.middleware.audit import AuditMiddleware

settings = get_settings()
configure_logging()

REQUESTS = Counter("astrosynth_requests_total", "Total HTTP requests", ["path"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("astrosynth_startup", version=__version__, env=settings.APP_ENV)
    # Warm the model so first /predict is fast
    from app.services.predictor import get_model

    get_model()
    yield
    logger.info("astrosynth_shutdown")


app = FastAPI(
    title="AstroSynth API",
    version=__version__,
    description="AI-powered exoplanet discovery platform",
    lifespan=lifespan,
)
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/metrics-prom")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    return {
        "name": "AstroSynth API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
