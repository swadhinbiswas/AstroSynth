"""Persistence tests. These skip unless a database is reachable.

Run with Postgres up:
    docker compose up -d postgres
    cd backend && alembic upgrade head && pytest tests/test_persistence.py -v
"""
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import engine

SAMPLE = {
    "orbital_period": 12.5,
    "transit_duration": 3.2,
    "planet_radius": 2.1,
    "stellar_radius": 0.95,
    "stellar_mass": 0.9,
    "stellar_temp": 5600,
    "transit_depth": 1200,
    "snr": 45,
    "semi_major_axis": 0.11,
    "equilibrium_temp": 800,
}


def _db_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _db_reachable(), reason="no database reachable")


from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_prediction_is_written_and_counted():
    before = client.get("/api/v1/predictions/stats").json()["total"]
    r = client.post("/api/v1/predict", json=SAMPLE)
    assert r.status_code == 200
    after = client.get("/api/v1/predictions/stats").json()["total"]
    assert after > before


def test_prediction_row_matches_response():
    r = client.post("/api/v1/predict", json=SAMPLE)
    body = r.json()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "select predicted_class, confidence from predictions "
                "order by created_at desc limit 1"
            )
        ).one()
    assert row.predicted_class == body["predicted_class"]
    assert abs(float(row.confidence) - body["confidence"]) < 0.001


def test_feedback_is_stored():
    r = client.post(
        "/api/v1/feedback",
        json={"user_label": "FALSE POSITIVE", "comment": "test row"},
    )
    body = r.json()
    assert body["stored"] is True
    assert body["total"] >= 1


def test_feedback_links_to_prediction():
    """A feedback row with a prediction_id must satisfy the foreign key."""
    with engine.connect() as conn:
        pred_id = conn.execute(text("select id from predictions limit 1")).scalar()
    if pred_id is None:
        pytest.skip("no predictions to link against")
    r = client.post(
        "/api/v1/feedback",
        json={"prediction_id": str(pred_id), "user_label": "CANDIDATE", "comment": "linked"},
    )
    assert r.status_code == 200
    assert r.json()["stored"] is True


def test_feedback_tolerates_malformed_prediction_id():
    r = client.post(
        "/api/v1/feedback",
        json={"prediction_id": "not-a-uuid", "user_label": "CANDIDATE"},
    )
    assert r.status_code == 200
    assert r.json()["stored"] is True


def test_audit_log_accepts_entries():
    from app.db.session import SessionLocal
    from app.services.telemetry import record_audit

    db = SessionLocal()
    try:
        ok = record_audit(db, actor="pytest", action="test.action", resource="unit")
        assert ok is True
    finally:
        db.close()
    with engine.connect() as conn:
        n = conn.execute(
            text("select count(*) from audit_logs where action = 'test.action'")
        ).scalar()
    assert n >= 1


def test_role_constraint_rejects_bad_role():
    """The CHECK constraint on users.role must hold at the database level."""
    with engine.begin() as conn:
        with pytest.raises(Exception):
            conn.execute(
                text(
                    "insert into users (id, email, password_hash, role) "
                    "values (:id, :email, 'x', 'superuser')"
                ),
                {"id": uuid.uuid4(), "email": f"bad-{uuid.uuid4()}@example.com"},
            )


def test_confidence_check_constraint():
    """predictions.confidence is constrained to 0..1."""
    with engine.begin() as conn:
        with pytest.raises(Exception):
            conn.execute(
                text(
                    "insert into predictions (input_features, predicted_class, confidence) "
                    "values ('{}'::jsonb, 'CONFIRMED', 1.5)"
                )
            )
