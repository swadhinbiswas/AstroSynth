"""Explainability helpers: global importance + SHAP summary data."""
import numpy as np


def global_importance(model, feature_names: list[str]) -> list[dict]:
    imp = getattr(model, "feature_importances_", None)
    if imp is None:
        imp = np.ones(len(feature_names)) / len(feature_names)
    ranked = sorted(zip(feature_names, imp), key=lambda t: float(t[1]), reverse=True)
    return [{"feature": f, "importance": round(float(v), 4)} for f, v in ranked]
