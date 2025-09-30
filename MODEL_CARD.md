# Model Card — astrosynth-catboost 1.0.0

- **Task**: 3-class transit disposition (CONFIRMED / CANDIDATE / FALSE POSITIVE).
- **Inputs**: 10 validated photometric + stellar features.
- **Metrics (held-out 20%)**: acc 0.941 · prec 0.937 · rec 0.933 · F1 0.935 · ROC-AUC 0.982.
- **Intended use**: triage + education; not a discovery claim. Confirm with follow-up observations.
- **Out of scope**: non-transiting planets (RV/direct imaging), pixel-level centroid vetting.
- **Risks**: training priors reflect Kepler field; TESS bright-star domain may shift. Monitor `/feedback` corrections.
- **Reproduce**: `python ml/scripts/train.py --config ml/configs/base.yaml` → `ml/artifacts/registry.json`.
