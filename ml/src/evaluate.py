"""Evaluation: accuracy / precision / recall / F1 / ROC-AUC + leaderboard markdown."""

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def _scores(y_true, y_pred, y_proba):
    out = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
    }
    try:
        out["roc_auc"] = round(float(roc_auc_score(y_true, y_proba, multi_class="ovr")), 4)
    except Exception:
        out["roc_auc"] = 0.0
    return out


def evaluate_all(results: dict) -> dict:
    metrics = {name: _scores(r["y_true"], r["y_pred"], r["y_proba"]) for name, r in results.items()}
    best = max(metrics, key=lambda k: metrics[k]["f1"])
    return {"metrics": metrics, "best_model": best}
