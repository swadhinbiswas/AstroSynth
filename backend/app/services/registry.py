"""Read whatever the training run actually produced.

The leaderboard is only as honest as the registry it reads from. When
`ml/artifacts/registry.json` exists we serve those metrics; when it does not we
say so instead of inventing numbers.
"""
import json
from functools import lru_cache
from pathlib import Path

REGISTRY_CANDIDATES = [
    Path(__file__).resolve().parents[3] / "ml" / "artifacts" / "registry.json",
    Path("/app/ml_artifacts/registry.json"),
    Path("ml/artifacts/registry.json"),
]

# Pretty names for the metrics table
DISPLAY = {
    "random_forest": "RandomForest",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
}


@lru_cache(maxsize=1)
def load_registry() -> dict | None:
    for p in REGISTRY_CANDIDATES:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:  # noqa: BLE001
                return None
    return None


def leaderboard_rows() -> list[dict]:
    """One row per model in the registry, sorted by F1. Empty if untrained."""
    reg = load_registry()
    if not reg:
        return []
    metrics = reg.get("metrics") or {}
    rows = []
    for key, m in metrics.items():
        rows.append(
            {
                "model": DISPLAY.get(key, key),
                "key": key,
                "version": "1.0.0",
                "accuracy": m.get("accuracy"),
                "precision": m.get("precision"),
                "recall": m.get("recall"),
                "f1": m.get("f1"),
                "roc_auc": m.get("roc_auc"),
                "is_best": key == reg.get("best_model"),
            }
        )
    return sorted(rows, key=lambda r: (r["f1"] is None, -(r["f1"] or 0)))


def registry_meta() -> dict:
    reg = load_registry() or {}
    return {
        "trained_at": reg.get("trained_at"),
        "best_model": reg.get("best_model"),
        "model_count": len(reg.get("metrics") or {}),
    }
