# Research Methodology

## Problem

Transit surveys produce far more threshold-crossing events than humans can vet by hand.
Kepler's cumulative table alone holds 9,201 KOI rows, and most are not planets: eclipsing
binaries, background blends, and instrumental systematics all produce transit-shaped dips.
The task is triage. Given catalog measurements for one event, decide whether it looks like a
confirmed planet, a candidate worth follow-up, or a false positive.

## Data

Real KOI data from the NASA Exoplanet Archive TAP service (`cumulative` table), fetched by
`ml/scripts/download_nasa.py`:

| Class | Rows | Share |
|---|---|---|
| FALSE POSITIVE | 4,582 | 49.8% |
| CONFIRMED | 2,746 | 29.8% |
| CANDIDATE | 1,873 | 20.4% |
| **Total** | **9,201** | |

Rows missing any required column are dropped at ingest rather than imputed at source.

## Features

Ten catalog measurements, listed in `ml/src/features.py`:

`koi_period` → `orbital_period`, `koi_duration` → `transit_duration`, `koi_prad` →
`planet_radius`, `koi_srad` → `stellar_radius`, `koi_smass` → `stellar_mass`, `koi_steff` →
`stellar_temp`, `koi_depth` → `transit_depth`, `koi_model_snr` → `snr`, `koi_sma` →
`semi_major_axis`, `koi_teq` → `equilibrium_temp`.

Four derived features encode relationships the raw columns hide:

| Feature | Formula | Rationale |
|---|---|---|
| `snr_per_depth` | `snr / (depth + 1)` | Separates a clean shallow transit from a noisy deep one |
| `log_period` | `log1p(period)` | Periods span 0.2 to 2000 days; the log compresses that range |
| `radius_ratio` | `R_p / (R★ × 109.2)` | Planet-to-star size ratio, which is what the transit depth measures |
| `temp_ratio` | `T_eq / T★` | Insolation balance, independent of absolute scale |

## Pipeline

1. **Ingest.** TAP query, rename columns, coerce numerics, drop rows without a disposition.
2. **Clean.** Median imputation, then clip to physical bounds. Values outside the bounds are
   clipped, not dropped, so a mislabelled unit does not delete a real detection.
3. **Split.** Stratified 80/20 before any fitting, so imputation and clipping statistics come
   from training data only.
4. **Tune.** Optuna TPE search, 30 trials per model, maximising weighted F1 on a validation
   carve-out. Search spaces live in `ml/src/tune.py`.
5. **Train.** Four candidates: RandomForest, XGBoost, LightGBM, CatBoost, each with class
   balancing (`class_weight="balanced"` or `auto_class_weights="Balanced"`).
6. **Evaluate.** Accuracy, weighted precision/recall/F1, and one-vs-rest ROC-AUC on the
   held-out set.
7. **Explain.** SHAP TreeExplainer for per-feature attributions. When `shap` is not installed
   the API returns deterministic permutation attributions and labels the method accordingly,
   so a consumer can always tell which one it got.
8. **Register.** Metrics, config, dataset provenance and the best model name go to
   `ml/artifacts/registry.json`. The API reads that file; it does not hold its own copy.

## Results

Held-out 20%, seed 42, 30 Optuna trials each:

| Model | Acc | Prec | Rec | F1 | ROC-AUC |
|---|---|---|---|---|---|
| XGBoost | 0.784 | 0.780 | 0.784 | **0.782** | 0.920 |
| CatBoost | 0.774 | 0.789 | 0.774 | 0.779 | 0.914 |
| LightGBM | 0.775 | 0.778 | 0.775 | 0.776 | 0.914 |
| RandomForest | 0.764 | 0.779 | 0.764 | 0.769 | 0.911 |

## What these numbers mean

F1 around 0.78 is a realistic result for photometric triage, in line with published
Kepler vetting classifiers (for example, Shallue & Vanderburg 2018 report comparable
accuracy on a harder task using raw light curves; ExoMiner, Valizadegan et al. 2022,
reaches higher precision with a deeper architecture and more inputs). Anyone quoting
above 0.95 on this feature set should be checked for leakage.

The model is better at separating FALSE POSITIVE from the rest than at distinguishing
CONFIRMED from CANDIDATE, which is expected: that boundary is partly a function of how
much follow-up effort an object has received, not of its photometry.

## Limitations

- Catalog features only; no light-curve shape information.
- Kepler-field training prior; TESS stars differ in brightness and noise.
- `CANDIDATE` is an operational label, not a physical one, which caps the ceiling.
- Synthetic-fixture metrics in the repo are meaningless by construction. `registry.json`
  records `is_synthetic` so the two runs are never confused.

## Reproducing

```bash
python ml/scripts/download_nasa.py --out data/raw
python ml/scripts/train.py --config ml/configs/base.yaml --input data/raw/koi_train.csv
```
