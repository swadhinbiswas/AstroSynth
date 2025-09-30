"""Tests that exercise the code paths which do not need a database.

The API is designed to serve predictions with or without Postgres, so these
tests must pass on a bare checkout. Anything asserting persistence lives in
`test_persistence.py`, which skips itself when no database is reachable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app
from app.services.predictor import FEATURE_ORDER

client = TestClient(app)

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


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_missions():
    r = client.get("/api/v1/missions")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 3
    assert {m["id"] for m in body["missions"]} == {"kepler", "k2", "tess"}


def test_datasets_filter_by_mission():
    everything = client.get("/api/v1/datasets").json()
    assert everything["count"] == 3
    only_kepler = client.get("/api/v1/datasets?mission=kepler").json()
    assert only_kepler["count"] == 1
    assert only_kepler["datasets"][0]["mission"] == "kepler"


def test_predict_returns_valid_distribution():
    r = client.post("/api/v1/predict", json=SAMPLE)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["predicted_class"] in ("CONFIRMED", "CANDIDATE", "FALSE POSITIVE")
    assert 0.0 <= body["confidence"] <= 1.0
    assert set(body["probabilities"]) == {"CONFIRMED", "CANDIDATE", "FALSE POSITIVE"}
    assert abs(sum(body["probabilities"].values()) - 1.0) < 0.02


def test_predict_includes_explanations_for_every_feature():
    r = client.post("/api/v1/predict", json=SAMPLE)
    body = r.json()
    assert body["explanations"]["method"] in ("shap-tree-explainer", "permutation-fallback")
    explained = {v["feature"] for v in body["explanations"]["values"]}
    # All ten contract features must be explained. A model trained with the
    # derived features also reports those, so assert a superset rather than
    # equality.
    assert set(FEATURE_ORDER).issubset(explained)
    assert len(explained) >= len(FEATURE_ORDER)


def test_predict_rejects_out_of_range_value():
    r = client.post("/api/v1/predict", json={**SAMPLE, "orbital_period": -5})
    assert r.status_code == 422


def test_predict_rejects_extra_field():
    """extra='forbid' turns a misspelled column into a 422, not a silent default."""
    r = client.post("/api/v1/predict", json={**SAMPLE, "unknown_column": 1})
    assert r.status_code == 422


def test_predict_rejects_missing_field():
    incomplete = {k: v for k, v in SAMPLE.items() if k != "snr"}
    r = client.post("/api/v1/predict", json=incomplete)
    assert r.status_code == 422


def test_batch_predict_two_rows():
    r = client.post("/api/v1/batch-predict", json={"rows": [SAMPLE, SAMPLE]})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 2
    assert len(body["results"]) == 2


def test_batch_rejects_empty_list():
    r = client.post("/api/v1/batch-predict", json={"rows": []})
    assert r.status_code == 422


def test_leaderboard_reports_training_state_honestly():
    r = client.get("/api/v1/leaderboard")
    assert r.status_code == 200
    body = r.json()
    assert "models" in body and "trained" in body
    if not body["trained"]:
        # Untrained must say so rather than serve invented scores.
        assert body["models"] == []
        assert body["note"]


def test_leaderboard_rows_carry_all_metrics():
    body = client.get("/api/v1/leaderboard").json()
    for row in body["models"]:
        for metric in ("accuracy", "precision", "recall", "f1", "roc_auc"):
            assert metric in row


def test_metrics_endpoint():
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    assert "prometheus_endpoint" in r.json()


def test_model_info_lists_ten_features():
    r = client.get("/api/v1/model-info")
    assert r.status_code == 200
    assert len(r.json()["features"]) == 10


def test_feedback_accepts_valid_label():
    r = client.post("/api/v1/feedback", json={"user_label": "CONFIRMED", "comment": "looks right"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_feedback_rejects_unknown_label():
    r = client.post("/api/v1/feedback", json={"user_label": "MAYBE"})
    assert r.status_code == 422


def test_prometheus_metrics_exposed():
    r = client.get("/metrics-prom")
    assert r.status_code == 200
    assert len(r.content) > 0


def test_prediction_stats_never_500s_without_db():
    """Predictions work without Postgres, so this endpoint must degrade cleanly."""
    r = client.get("/api/v1/predictions/stats")
    assert r.status_code == 200
    assert "counts" in r.json()


def test_root_lists_docs_and_health():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["docs"] == "/docs"
    assert "health" in body
