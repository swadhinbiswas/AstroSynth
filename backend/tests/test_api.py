import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE = {
    "orbital_period": 12.5, "transit_duration": 3.2, "planet_radius": 2.1,
    "stellar_radius": 0.95, "stellar_mass": 0.9, "stellar_temp": 5600,
    "transit_depth": 1200, "snr": 45, "semi_major_axis": 0.11, "equilibrium_temp": 800,
}


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_missions():
    r = client.get("/api/v1/missions")
    assert r.json()["count"] == 3


def test_predict():
    r = client.post("/api/v1/predict", json=SAMPLE)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["predicted_class"] in ("CONFIRMED", "CANDIDATE", "FALSE POSITIVE")
    assert 0 <= body["confidence"] <= 1
    assert "explanations" in body


def test_predict_validation():
    bad = dict(SAMPLE); bad["orbital_period"] = -5
    r = client.post("/api/v1/predict", json=bad)
    assert r.status_code == 422


def test_batch():
    r = client.post("/api/v1/batch-predict", json={"rows": [SAMPLE, SAMPLE]})
    assert r.json()["count"] == 2


def test_leaderboard():
    r = client.get("/api/v1/leaderboard")
    assert len(r.json()["models"]) == 4


def test_feedback():
    r = client.post("/api/v1/feedback", json={"user_label": "CONFIRMED", "comment": "looks good"})
    assert r.json()["ok"] is True
