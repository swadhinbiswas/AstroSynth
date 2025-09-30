# Research Methodology

## Problem
Transit surveys produce thousands of threshold-crossing events; most are astrophysical false positives (eclipsing binaries, systematics). Manual vetting does not scale to Kepler (9.5k KOIs) + K2 + TESS (7k+ TOIs).

## Data
NASA Exoplanet Archive cumulative KOI DR25, K2 candidates, TESS TOI catalog. 10 core features capture transit shape (period, duration, depth, SNR), planet size, stellar context and orbit energetics.

## Method
1. **Validation**: range checks per feature; missing → median; outliers clipped to physical bounds (never silently dropped).
2. **Features**: +4 derived (`snr_per_depth`, `log_period`, `radius_ratio`, `temp_ratio`) encoding SNR efficiency and star–planet geometry.
3. **Imbalance**: stratified split + `class_weight=balanced` / `auto_class_weights`.
4. **Models**: RF (baseline), XGBoost, LightGBM, CatBoost; Optuna search (30 trials) over depth/lr/estimators.
5. **Evaluation**: accuracy, precision, recall, weighted F1, OvR ROC-AUC; leaderboard promotes best F1.
6. **Explainability**: SHAP TreeExplainer globally + per-decision waterfall; permutation fallback guarantees availability.

## Limits
Photometry-only — no pixel-level vetting, no follow-up spectra. SNR-driven heuristics bias toward deep transits; small rocky planets in noisy stars remain hard. See `MODEL_CARD.md`.
