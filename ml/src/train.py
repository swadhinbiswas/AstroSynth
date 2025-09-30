"""Train RF / XGBoost / LightGBM / CatBoost with class-balanced defaults.

When Optuna is installed and `trials > 0`, each candidate is tuned on a
validation split first; otherwise the defaults below are used.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.features import TARGET, all_features
from src.tune import tune_model

# Canonical class order used by the API contract. Keep in sync with
# backend/app/services/predictor.py CLASSES.
CLASS_ORDER = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
CLASS_TO_ID = {c: i for i, c in enumerate(CLASS_ORDER)}

# Fallback parameters, used when Optuna is unavailable or trials == 0.
DEFAULTS: dict[str, dict] = {
    "random_forest": {"n_estimators": 300, "max_depth": 16},
    "xgboost": {"n_estimators": 300, "max_depth": 8, "learning_rate": 0.06, "subsample": 0.9, "colsample_bytree": 0.9},
    "lightgbm": {"n_estimators": 300, "learning_rate": 0.06},
    "catboost": {"iterations": 400, "depth": 8, "learning_rate": 0.06},
}


def _build(model_name: str, params: dict, seed: int):
    """Instantiate one candidate, or return None when its library is missing."""
    try:
        if model_name == "random_forest":
            return RandomForestClassifier(class_weight="balanced", random_state=seed, n_jobs=-1, **params)
        if model_name == "xgboost":
            from xgboost import XGBClassifier

            return XGBClassifier(eval_metric="mlogloss", random_state=seed, n_jobs=-1, **params)
        if model_name == "lightgbm":
            from lightgbm import LGBMClassifier

            return LGBMClassifier(class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1, **params)
        if model_name == "catboost":
            from catboost import CatBoostClassifier

            return CatBoostClassifier(auto_class_weights="Balanced", random_seed=seed, verbose=False, **params)
    except ImportError as e:
        print(f"[train] {model_name} unavailable: {e}")
    return None


def _get_candidates(seed: int, trials: int, X=None, y=None):
    """Fit-ready candidates. Tuning happens here so callers stay simple."""
    models: dict = {}
    for name, default_params in DEFAULTS.items():
        params = dict(default_params)
        if trials > 0 and X is not None and y is not None:
            best = tune_model(name, X, y, trials=trials, seed=seed)
            if best:
                params = {**params, **best}
        clf = _build(name, params, seed)
        if clf is not None:
            models[name] = clf
    return models


def train_all(df, test_size: float = 0.2, seed: int = 42, trials: int = 0):
    feats = all_features()
    X = df[feats].to_numpy(dtype=float)
    y = df[TARGET].astype(str).map(CLASS_TO_ID).to_numpy(dtype=int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)

    candidates = _get_candidates(seed, trials, X=Xtr, y=ytr)
    if not candidates:
        raise RuntimeError("No models available. Install scikit-learn at minimum.")

    results, artifacts = {}, {}
    for name, clf in candidates.items():
        clf.fit(Xtr, ytr)
        pred = clf.predict(Xte)
        proba = clf.predict_proba(Xte) if hasattr(clf, "predict_proba") else None
        results[name] = {
            "y_true": yte,
            "y_pred": np.asarray(pred),
            "y_proba": np.asarray(proba) if proba is not None else None,
            "labels": list(CLASS_ORDER),
        }
        artifacts[name] = clf
        print(f"[train] {name} done")
    return results, artifacts
