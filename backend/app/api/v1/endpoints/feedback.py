"""Feedback capture. Labels land in the `feedback` table when Postgres is up.

The table is the retraining signal: `user_label` records what a human thinks the
true class was, so a future run can compare it against what the model predicted.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import FeedbackRequest

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
def submit_feedback(body: FeedbackRequest, db: Session = Depends(get_db)):
    """Store one label. Returns `stored: false` when no database is reachable."""
    payload = body.model_dump()
    stored = False
    total = None
    try:
        from sqlalchemy import func, select

        from app.models import Feedback

        pred_id = None
        if payload.get("prediction_id"):
            try:
                pred_id = uuid.UUID(str(payload["prediction_id"]))
            except ValueError:
                pred_id = None

        db.add(
            Feedback(
                prediction_id=pred_id,
                user_label=payload["user_label"],
                comment=payload.get("comment", ""),
            )
        )
        db.commit()
        total = db.execute(select(func.count()).select_from(Feedback)).scalar()
        stored = True
    except Exception:  # noqa: BLE001 - never fail a user's feedback submission
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass

    return {
        "ok": True,
        "stored": stored,
        "total": total,
        "message": "Thanks. Your label is recorded for the next training run."
        if stored
        else "Received. Start Postgres to persist labels for retraining.",
    }


@router.get("/feedback")
def list_feedback(limit: int = Query(default=50, le=200), db: Session = Depends(get_db)):
    try:
        from sqlalchemy import desc, select

        from app.models import Feedback

        rows = db.execute(select(Feedback).order_by(desc(Feedback.created_at)).limit(limit)).scalars().all()
        items = [
            {
                "id": str(r.id),
                "prediction_id": str(r.prediction_id) if r.prediction_id else None,
                "user_label": r.user_label,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
        return {"count": len(items), "items": items}
    except Exception:  # noqa: BLE001
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass
        return {"count": 0, "items": [], "note": "Database unavailable."}
