# AstroSynth API

Base: `http://localhost:8000/api/v1` · Interactive: `/docs`

## POST /predict

```bash
curl -X POST localhost:8000/api/v1/predict -H 'Content-Type: application/json' -d '{
  "orbital_period": 12.5, "transit_duration": 3.2, "planet_radius": 2.1,
  "stellar_radius": 0.95, "stellar_mass": 0.9, "stellar_temp": 5600,
  "transit_depth": 1200, "snr": 45, "semi_major_axis": 0.11, "equilibrium_temp": 800
}'
```

Response: `{predicted_class, confidence, probabilities, explanations{method, values[], waterfall[]}, model_name, model_version}`.

## POST /batch-predict

`{"rows": [{...}, ...]}` — max 1000 rows; CSV and JSON are parsed client-side in Prediction Studio.

## Others

- `GET /missions`, `GET /datasets?mission=kepler`, `GET /leaderboard`, `GET /metrics`, `GET /model-info`, `GET /health`, `POST /feedback`, `POST /auth/login|register`, `GET /me`.
- Errors: `422` validation (Pydantic), `429` rate limit, `401/403` auth. All errors are JSON `{detail}`.
