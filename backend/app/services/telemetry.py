"""Prediction and audit persistence, with a circuit breaker.

Every prediction would otherwise attempt a database write. When Postgres is not
running, each attempt costs a full TCP timeout, so a demo without a database
drags. The breaker opens after the first failure and stays open for a cooldown,
turning that cost into a single check.

Nothing here can fail a request: the prediction is already computed and is
returned regardless of what the database does.
"""
import time
from typing import Any

from app.core.logging import logger

# Circuit breaker state. Opened on the first persistence failure, re-tried after
# the cooldown. Shared across threads; a benign race just means an extra attempt.
_DB_OK = True
_RETRY_AFTER = 0.0
_COOLDOWN_SECONDS = 60.0


def db_available() -> bool:
    """True when persistence should be attempted."""
    global _DB_OK, _RETRY_AFTER
    if _DB_OK:
        return True
    if time.time() >= _RETRY_AFTER:
        _DB_OK = True  # cooldown elapsed, allow one attempt to prove recovery
        return True
    return False


def _trip(reason: str) -> None:
    global _DB_OK, _RETRY_AFTER
    if _DB_OK:
        logger.warning("persistence_disabled", reason=reason, retry_in_s=_COOLDOWN_SECONDS)
    _DB_OK = False
    _RETRY_AFTER = time.time() + _COOLDOWN_SECONDS


def record_prediction(
    db,
    *,
    user_id: Any | None,
    model_id: Any | None,
    input_features: dict,
    predicted_class: str,
    confidence: float,
    probabilities: dict,
    explanations: dict,
) -> bool:
    """Insert one prediction row. Returns True on success."""
    if db is None or not db_available():
        return False
    try:
        from app.models import Prediction

        db.add(
            Prediction(
                user_id=user_id,
                model_id=model_id,
                input_features=input_features,
                predicted_class=predicted_class,
                confidence=confidence,
                probabilities=probabilities,
                explanations=explanations,
            )
        )
        db.commit()
        return True
    except Exception as e:  # noqa: BLE001
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass
        _trip(str(e)[:120])
        return False


def record_audit(db, *, actor: str, action: str, resource: str, meta: dict | None = None) -> bool:
    if db is None or not db_available():
        return False
    try:
        from app.models import AuditLog

        db.add(AuditLog(actor=actor, action=action, resource=resource, meta=meta or {}))
        db.commit()
        return True
    except Exception as e:  # noqa: BLE001
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass
        _trip(str(e)[:120])
        return False


def prediction_counts(db) -> dict:
    """Return {class: count}. Empty when persistence is unavailable."""
    if db is None or not db_available():
        return {}
    try:
        from sqlalchemy import func, select

        from app.models import Prediction

        rows = db.execute(
            select(Prediction.predicted_class, func.count()).group_by(Prediction.predicted_class)
        ).all()
        return {cls: int(n) for cls, n in rows}
    except Exception as e:  # noqa: BLE001
        _trip(str(e)[:120])
        return {}
