"""Model loading + inference. Falls back to a synthetic-trained RF if no artifact exists."""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.core.logging import logger

CLASSES = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
FEATURE_ORDER = [
    "orbital_period",
    "transit_duration",
    "planet_radius",
    "stellar_radius",
    "stellar_mass",
    "stellar_temp",
    "transit_depth",
    "snr",
    "semi_major_axis",
    "equilibrium_temp",
]
# Full 14-feature order used by production artifacts (10 base + 4 engineered).
# Must match ml/src/features.py::all_features().
FULL_ORDER = FEATURE_ORDER + [
    "snr_per_depth",
    "log_period",
    "radius_ratio",
    "temp_ratio",
]
MODEL_NAME = "astrosynth-rf"
MODEL_VERSION = "1.0.0"

ARTIFACT_CANDIDATES = [
    Path(__file__).resolve().parents[3] / "ml" / "artifacts" / "model_rf.joblib",
    Path("/app/ml_artifacts/model_rf.joblib"),
    Path("ml/artifacts/model_rf.joblib"),
]


def _train_fallback() -> RandomForestClassifier:
    rng = np.random.default_rng(42)
    n = 1500
    X = np.column_stack(
        [
            rng.uniform(0.5, 500, n),  # orbital_period
            rng.uniform(0.5, 15, n),  # transit_duration
            rng.uniform(0.3, 20, n),  # planet_radius
            rng.uniform(0.3, 3.0, n),  # stellar_radius
            rng.uniform(0.3, 2.0, n),  # stellar_mass
            rng.uniform(3000, 7500, n),  # stellar_temp
            rng.uniform(10, 20000, n),  # transit_depth
            rng.uniform(5, 200, n),  # snr
            rng.uniform(0.01, 2.0, n),  # semi_major_axis
            rng.uniform(100, 2500, n),  # equilibrium_temp
        ]
    )
    # Physics-flavoured heuristic labels so demo predictions look sensible.
    y = np.where(
        (X[:, 7] > 25) & (X[:, 6] > 200) & (X[:, 2] < 12),
        0,
        np.where((X[:, 7] > 10) & (X[:, 2] < 18), 1, 2),
    )
    clf = RandomForestClassifier(n_estimators=200, max_depth=14, random_state=42, n_jobs=-1)
    clf.fit(X, y)
    logger.info("trained_fallback_model", n=n)
    return clf


@lru_cache(maxsize=1)
def get_model():
    for p in ARTIFACT_CANDIDATES:
        if p.exists():
            logger.info("loading_model_artifact", path=str(p))
            return joblib.load(p)
    return _train_fallback()


def _engineer_row(features: dict) -> dict:
    """Mirror ml/src/features.py engineering so serving matches training."""
    f = dict(features)
    f["snr_per_depth"] = f["snr"] / (f["transit_depth"] + 1)
    f["log_period"] = float(np.log1p(f["orbital_period"]))
    f["radius_ratio"] = f["planet_radius"] / (f["stellar_radius"] * 109.2 + 1e-6)
    f["temp_ratio"] = f["equilibrium_temp"] / (f["stellar_temp"] + 1e-6)
    return f


def _vector_for(model, features: dict) -> np.ndarray:
    want = int(getattr(model, "n_features_in_", len(FEATURE_ORDER)))
    if want == len(FULL_ORDER):
        full = _engineer_row(features)
        return np.array([[full[k] for k in FULL_ORDER]], dtype=float)
    return np.array([[features[k] for k in FEATURE_ORDER]], dtype=float)


def predict_proba(features: dict) -> tuple[str, float, dict[str, float]]:
    model = get_model()
    x = _vector_for(model, features)
    proba = model.predict_proba(x)[0]
    # Training uses canonical CLASS_ORDER ids 0/1/2 == CLASSES, so align by position.
    classes = list(getattr(model, "classes_", [0, 1, 2]))
    probs: dict[str, float] = {}
    for cls_id, p in zip(classes, proba):
        try:
            probs[CLASSES[int(cls_id)]] = float(p)
        except (ValueError, IndexError):
            probs[str(cls_id)] = float(p)
    for c in CLASSES:
        probs.setdefault(c, 0.0)
    best = max(probs, key=lambda k: probs[k])
    return best, float(probs[best]), probs


def feature_importance_global() -> list[dict]:
    model = get_model()
    want = int(getattr(model, "n_features_in_", len(FEATURE_ORDER)))
    names = FULL_ORDER if want == len(FULL_ORDER) else FEATURE_ORDER
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        importances = [1.0 / len(names)] * len(names)
    ranked = sorted(zip(names, importances), key=lambda t: t[1], reverse=True)
    return [{"feature": f, "importance": round(float(v), 4)} for f, v in ranked]
