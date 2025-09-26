"""Lightweight SHAP-style explanations without hard SHAP dependency at request time.

Tries `shap` if installed; otherwise returns a deterministic permutation-based
attribution so the API never 500s on explainability.
"""

import numpy as np

from app.services.predictor import FEATURE_ORDER, get_model, predict_proba


def explain_local(features: dict, nsamples: int = 200) -> dict:
    try:
        import shap  # noqa: F401

        return _shap_explain(features)
    except Exception:
        return _permutation_explain(features)


def _permutation_explain(features: dict) -> dict:
    base_vec = np.array([features[k] for k in FEATURE_ORDER], dtype=float)
    _, _, base_proba = predict_proba(features)
    pred_class = max(base_proba, key=lambda k: base_proba[k])
    base_p = base_proba[pred_class]
    scales = np.abs(base_vec) + 1e-6
    contribs = []
    for i, name in enumerate(FEATURE_ORDER):
        perturbed = base_vec.copy()
        perturbed[i] = base_vec[i] + 0.15 * scales[i]
        f2 = dict(zip(FEATURE_ORDER, perturbed.tolist()))
        _, _, p2 = predict_proba(f2)
        delta = float(p2.get(pred_class, 0.0) - base_p)
        contribs.append(
            {
                "feature": name,
                "value": float(base_vec[i]),
                "shap_value": round(delta, 5),
            }
        )
    contribs.sort(key=lambda d: abs(d["shap_value"]), reverse=True)
    return {
        "method": "permutation-fallback",
        "predicted_class": pred_class,
        "base_probability": round(base_p, 4),
        "values": contribs,
        "waterfall": [{"feature": c["feature"], "contribution": c["shap_value"]} for c in contribs],
    }


def _shap_explain(features: dict) -> dict:
    import shap

    from app.services.predictor import FULL_ORDER, _vector_for

    model = get_model()
    x = _vector_for(model, features)
    names = FULL_ORDER if x.shape[1] == len(FULL_ORDER) else FEATURE_ORDER
    try:
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(x)
        if isinstance(sv, list):
            sv = np.array(sv)[:, 0, :]
        sv = np.asarray(sv).reshape(-1)
    except Exception:
        return _permutation_explain(features)
    _, _, proba = predict_proba(features)
    pred_class = max(proba, key=lambda k: proba[k])
    vals = [
        {"feature": f, "value": float(v), "shap_value": round(float(s), 5)}
        for f, v, s in zip(names, x[0].tolist(), sv.tolist())
    ]
    vals.sort(key=lambda d: abs(d["shap_value"]), reverse=True)
    return {
        "method": "shap-tree-explainer",
        "predicted_class": pred_class,
        "base_probability": round(float(proba[pred_class]), 4),
        "values": vals,
        "waterfall": [{"feature": c["feature"], "contribution": c["shap_value"]} for c in vals],
    }
