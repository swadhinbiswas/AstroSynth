"""Optuna hyperparameter search over the candidate models.

Each study maximises weighted F1 on a held-out validation split carved from
the training data. Trials are logged to stdout and the best parameters are
returned for the caller to fit a final model on the full training set.

If Optuna is not installed the caller falls back to the default parameters in
`train.py`, so training still works on a bare install.
"""

from __future__ import annotations

from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

try:
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without optuna
    OPTUNA_AVAILABLE = False


def suggest_params(trial, model_name: str) -> dict:
    """Search space per algorithm. Bounds are wide enough to be useful and
    narrow enough that 30 trials land somewhere sensible."""
    if model_name == "random_forest":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 6, 24),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 8),
        }
    if model_name == "xgboost":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        }
    if model_name == "lightgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=50),
            "num_leaves": trial.suggest_int("num_leaves", 15, 127),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 60),
        }
    if model_name == "catboost":
        return {
            "iterations": trial.suggest_int("iterations", 200, 800, step=100),
            "depth": trial.suggest_int("depth", 4, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        }
    return {}


def tune_model(model_name: str, X, y, trials: int, seed: int, verbose: bool = True) -> dict:
    """Return the best params found, or {} when Optuna is unavailable."""
    if not OPTUNA_AVAILABLE or trials <= 0:
        return {}

    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)

    def objective(trial) -> float:
        params = suggest_params(trial, model_name)
        clf = _build(model_name, params, seed)
        if clf is None:
            return 0.0
        clf.fit(X_tr, y_tr)
        pred = clf.predict(X_val)
        return float(f1_score(y_val, pred, average="weighted", zero_division=0))

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=trials, show_progress_bar=False)
    if verbose:
        print(f"[tune] {model_name}: best F1={study.best_value:.4f} params={study.best_params}")
    return dict(study.best_params)


def _build(model_name: str, params: dict, seed: int):
    """Instantiate a model with the given params, or None if the lib is missing."""
    try:
        if model_name == "random_forest":
            from sklearn.ensemble import RandomForestClassifier

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
    except ImportError:
        return None
    return None
