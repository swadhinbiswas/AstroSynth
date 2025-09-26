from fastapi import APIRouter, Query

from app.services.catalog import DATASETS, LEADERBOARD, MISSIONS

router = APIRouter(tags=["catalog"])


@router.get("/missions")
def list_missions():
    return {"count": len(MISSIONS), "missions": MISSIONS}


@router.get("/datasets")
def list_datasets(mission: str | None = Query(default=None)):
    rows = [d for d in DATASETS if mission is None or d["mission"] == mission]
    return {"count": len(rows), "datasets": rows}


@router.get("/leaderboard")
def leaderboard():
    return {"models": sorted(LEADERBOARD, key=lambda m: m["f1"], reverse=True)}


@router.get("/metrics")
def metrics():
    top = max(LEADERBOARD, key=lambda m: m["f1"])
    return {
        "active_model": top,
        "all": LEADERBOARD,
        "prometheus_endpoint": "/metrics-prom",
    }
