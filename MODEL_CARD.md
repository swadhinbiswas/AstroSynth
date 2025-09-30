# Model Card — astrosynth (XGBoost, best of four)

## What this model does

Predicts a transit disposition for one KOI: `CONFIRMED`, `CANDIDATE`, or `FALSE POSITIVE`.

## Training data

Real data from the [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) TAP
service, table `cumulative`:

| | |
|---|---|
| Rows | 9,201 |
| Source | `koi_train.csv`, fetched by `ml/scripts/download_nasa.py` |
| CONFIRMED | 2,746 |
| CANDIDATE | 1,873 |
| FALSE POSITIVE | 4,582 |
| Split | 80% train / 20% held-out test, stratified |
| Rows with nulls in required columns | dropped at ingest |

The synthetic fixture in `download_nasa.py` is for offline tests only. Metrics from
it are meaningless because the labels are a deterministic function of two columns;
the model recovers the rule exactly and scores near 1.0. `registry.json` records
`is_synthetic` so you can tell which run produced a number.

## Features

Ten raw measurements plus four derived: `snr_per_depth`, `log_period`,
`radius_ratio`, `temp_ratio`. Missing values are median-imputed, then clipped to
physical bounds (`ml/src/features.py`).

## Results (held-out 20%, seed 42, 30 Optuna trials per model)

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **XGBoost** | **0.784** | 0.780 | 0.784 | **0.782** | 0.920 |
| CatBoost | 0.774 | 0.789 | 0.774 | 0.779 | 0.914 |
| LightGBM | 0.775 | 0.778 | 0.775 | 0.776 | 0.914 |
| RandomForest | 0.764 | 0.779 | 0.764 | 0.769 | 0.911 |

Precision, recall and F1 are weighted averages across the three classes.

These are the numbers `ml/artifacts/registry.json` reports. The API serves that
file directly (`/api/v1/leaderboard`), so the figures in the UI cannot drift from
the run that produced them.

## Intended use

Triage and teaching: narrowing a large candidate list before a human looks at it,
and showing how a classifier's decision decomposes across physical features.

## Not intended for

- Claiming a discovery. Every output needs follow-up observation and independent vetting.
- Non-transiting planets (radial velocity, direct imaging, microlensing).
- Pixel-level vetting such as centroid analysis or difference imaging.

## Known limitations

- **Photometry only.** The model sees catalog values, not light curves. It cannot
  detect a background eclipsing binary that mimics a transit.
- **Label noise.** The archive's `CANDIDATE` class mixes real planets with
  unresolved false positives, which caps achievable accuracy.
- **Field bias.** Trained on Kepler-field KOIs. TESS observes brighter, nearer
  stars with different noise, so expect a domain shift.
- **Imbalance.** FALSE POSITIVE outnumbers CONFIRMED roughly 1.7:1. Weighted
  metrics hide this; check per-class recall before trusting a class you care about.

## Reproduce

```bash
python ml/scripts/download_nasa.py --out data/raw
python ml/scripts/train.py --config ml/configs/base.yaml --input data/raw/koi_train.csv
# writes ml/artifacts/registry.json and model_*.joblib
```

`optuna_trials: 30` in `ml/configs/base.yaml` controls the search budget. Set it to
0 for a fast run with the default parameters.
