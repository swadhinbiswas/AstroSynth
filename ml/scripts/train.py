"""Full training pipeline: clean -> engineer -> split -> train 4 models -> evaluate -> save best + registry entry.

Usage: python ml/scripts/train.py --config ml/configs/base.yaml [--input data/raw/synthetic_train.csv]
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evaluate import evaluate_all
from src.features import engineer
from src.train import train_all


REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve(p: str | Path) -> Path:
    p = Path(p)
    if p.is_absolute():
        return p
    # Allow running from repo root OR from ml/
    if (REPO_ROOT / p).exists() or not p.exists():
        # Prefer repo-root-relative when ambiguous (e.g. ml/artifacts, data/raw)
        candidate = REPO_ROOT / p
        if str(p).startswith("ml/") or str(p).startswith("data/"):
            return candidate
    return p


def load_frame(path: Path):
    import pandas as pd
    if path.exists():
        return pd.read_csv(path)
    from scripts.download_nasa import synthetic
    print(f"[train] {path} missing — using synthetic data")
    return synthetic()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ml/configs/base.yaml")
    ap.add_argument("--input", default="data/raw/synthetic_train.csv")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(_resolve(args.config)))
    df = load_frame(_resolve(args.input))
    df = engineer(df)

    results, artifacts = train_all(df, test_size=cfg.get("test_size", 0.2), seed=cfg.get("seed", 42))
    report = evaluate_all(results)

    art_dir = _resolve(cfg.get("artifacts_dir", "ml/artifacts"))
    art_dir.mkdir(parents=True, exist_ok=True)
    best_name = max(report["metrics"], key=lambda k: report["metrics"][k]["f1"])
    joblib.dump(artifacts[best_name], art_dir / "model_rf.joblib")
    for name, model in artifacts.items():
        joblib.dump(model, art_dir / f"model_{name}.joblib")

    registry_entry = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "metrics": report["metrics"],
        "best_model": best_name, "report": report,
    }
    (art_dir / "registry.json").write_text(json.dumps(registry_entry, indent=2))
    print(json.dumps(report, indent=2))
    print(f"[train] best={best_name} artifacts -> {art_dir}")


if __name__ == "__main__":
    main()
