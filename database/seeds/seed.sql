-- Demo seed data.
--
-- Note on model metrics: the leaderboard is served from
-- ml/artifacts/registry.json (written by `python ml/scripts/train.py`), not from
-- this file. The rows below only populate the models table so foreign keys and
-- the admin panel have something to reference. Metrics here are deliberately
-- left empty rather than invented; the registry is the source of truth.

INSERT INTO datasets (name, mission, version, rows_count, storage_uri, meta)
VALUES
    ('Kepler KOI DR25', 'kepler', 'DR25', 9564,
     'https://exoplanetarchive.ipac.caltech.edu/', '{"source": "NASA Exoplanet Archive"}'),
    ('K2 Planet Candidates', 'k2', 'v2024', 4896,
     'https://exoplanetarchive.ipac.caltech.edu/', '{"source": "NASA Exoplanet Archive"}'),
    ('TESS TOI Catalog', 'tess', '2024.10', 7000,
     'https://exoplanetarchive.ipac.caltech.edu/', '{"source": "NASA Exoplanet Archive"}')
ON CONFLICT DO NOTHING;

INSERT INTO models (name, version, algorithm, metrics, params, is_active)
VALUES
    ('astrosynth-random_forest', '1.0.0', 'RandomForest', '{}', '{}', false),
    ('astrosynth-xgboost', '1.0.0', 'XGBoost', '{}', '{}', false),
    ('astrosynth-lightgbm', '1.0.0', 'LightGBM', '{}', '{}', false),
    ('astrosynth-catboost', '1.0.0', 'CatBoost', '{}', '{}', false);
