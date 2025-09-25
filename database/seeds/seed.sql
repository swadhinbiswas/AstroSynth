-- Demo seeds: missions as datasets + leaderboard models + demo admin
INSERT INTO datasets (name, mission, version, rows_count, storage_uri, meta) VALUES
 ('Kepler KOI DR25','kepler','DR25',9564,'s3://astrosynth/kepler-koi-dr25.parquet','{"source":"NASA Exoplanet Archive"}'),
 ('K2 Planet Candidates','k2','v2024',4896,'s3://astrosynth/k2-candidates.parquet','{"source":"NASA Exoplanet Archive"}'),
 ('TESS TOI Catalog','tess','2024.10',7000,'s3://astrosynth/tess-toi.parquet','{"source":"NASA Exoplanet Archive"}')
ON CONFLICT DO NOTHING;

INSERT INTO models (name, version, algorithm, metrics, is_active) VALUES
 ('astrosynth-catboost','1.0.0','CatBoost','{"accuracy":0.941,"f1":0.935,"roc_auc":0.982}', true),
 ('astrosynth-xgboost','1.0.0','XGBoost','{"accuracy":0.938,"f1":0.932,"roc_auc":0.980}', false),
 ('astrosynth-lightgbm','1.0.0','LightGBM','{"accuracy":0.931,"f1":0.925,"roc_auc":0.977}', false),
 ('astrosynth-rf','1.0.0','RandomForest','{"accuracy":0.918,"f1":0.910,"roc_auc":0.968}', false);
