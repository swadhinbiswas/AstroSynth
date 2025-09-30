from fastapi import APIRouter, Query

from app.services.catalog import DATASETS, MISSIONS
from app.services.registry import leaderboard_rows, registry_meta

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
    rows = leaderboard_rows()
    return {
        "models": rows,
        "meta": registry_meta(),
        "trained": bool(rows),
        "note": None
        if rows
        else "No training run found. Run `python ml/scripts/train.py --config ml/configs/base.yaml`.",
    }


@router.get("/metrics")
def metrics():
    rows = leaderboard_rows()
    best = next((r for r in rows if r.get("is_best")), rows[0] if rows else None)
    return {
        "active_model": best,
        "all": rows,
        "meta": registry_meta(),
        "prometheus_endpoint": "/metrics-prom",
    }
