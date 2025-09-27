"""Train RF / XGBoost / LightGBM / CatBoost with class-balanced defaults."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.features import TARGET, all_features

# Canonical class order used by the API contract. Keep in sync with
# backend/app/services/predictor.py CLASSES.
CLASS_ORDER = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
CLASS_TO_ID = {c: i for i, c in enumerate(CLASS_ORDER)}


def _get_candidates(seed: int):
    models: dict = {"random_forest": RandomForestClassifier(n_estimators=300, max_depth=16, class_weight="balanced", random_state=seed, n_jobs=-1)}
    try:
        from xgboost import XGBClassifier
        models["xgboost"] = XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.06, subsample=0.9, colsample_bytree=0.9, eval_metric="mlogloss", random_state=seed, n_jobs=-1)
    except Exception as e:
        print(f"[train] xgboost unavailable: {e}")
    try:
        from lightgbm import LGBMClassifier
        models["lightgbm"] = LGBMClassifier(n_estimators=300, max_depth=-1, learning_rate=0.06, class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1)
    except Exception as e:
        print(f"[train] lightgbm unavailable: {e}")
    try:
        from catboost import CatBoostClassifier
        models["catboost"] = CatBoostClassifier(iterations=400, depth=8, learning_rate=0.06, auto_class_weights="Balanced", random_seed=seed, verbose=False)
    except Exception as e:
        print(f"[train] catboost unavailable: {e}")
    return models


def train_all(df, test_size: float = 0.2, seed: int = 42):
    feats = all_features()
    X = df[feats].to_numpy(dtype=float)
    y = df[TARGET].astype(str).map(CLASS_TO_ID).to_numpy(dtype=int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)
    results, artifacts = {}, {}
    for name, clf in _get_candidates(seed).items():
        clf.fit(Xtr, ytr)
        pred = clf.predict(Xte)
        proba = clf.predict_proba(Xte) if hasattr(clf, "predict_proba") else None
        results[name] = {"y_true": yte, "y_pred": np.asarray(pred), "y_proba": np.asarray(proba) if proba is not None else None, "labels": list(CLASS_ORDER)}
        artifacts[name] = clf
        print(f"[train] {name} done")
    return results, artifacts
