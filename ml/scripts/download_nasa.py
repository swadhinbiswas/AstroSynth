"""Fetch real KOI data from the NASA Exoplanet Archive TAP service.

This is the source of truth for training. The synthetic generator below exists
only for offline tests and CI; it is never used to produce the numbers in the
README.

TAP docs: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

TAP_SYNC = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

# Column names in the archive -> names this project uses.
COLUMN_MAP = {
    "koi_period": "orbital_period",
    "koi_duration": "transit_duration",
    "koi_prad": "planet_radius",
    "koi_srad": "stellar_radius",
    "koi_smass": "stellar_mass",
    "koi_steff": "stellar_temp",
    "koi_depth": "transit_depth",
    "koi_model_snr": "snr",
    "koi_sma": "semi_major_axis",
    "koi_teq": "equilibrium_temp",
    "koi_disposition": "disposition",
}

# koi_duration is in hours already; the rest are in the units we document.
QUERY = """
select {cols}
from cumulative
where koi_disposition is not null
  and koi_period is not null
  and koi_prad is not null
  and koi_model_snr is not null
""".format(cols=",".join(COLUMN_MAP))


def fetch_koi(limit: int | None = None, timeout: int = 180) -> pd.DataFrame:
    """Download the KOI cumulative table and rename columns. Raises on failure."""
    import requests

    url = f"{TAP_SYNC}?query={QUERY}&format=csv"
    if limit:
        url = f"{TAP_SYNC}?query=select+top+{limit}+*+from+cumulative&format=csv"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    from io import StringIO

    df = pd.read_csv(StringIO(r.text))
    return _normalise(df)


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_MAP)
    keep = [c for c in COLUMN_MAP.values() if c in df.columns]
    df = df[keep].copy()
    for c in keep:
        if c != "disposition":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["disposition"])
    # Archive uses these exact strings; anything else is dropped.
    df = df[df["disposition"].isin(["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"])]
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Synthetic fallback. Used by tests and CI only. The labels come from a fixed
# rule on two columns, so a model can recover the rule exactly and score near
# 1.0. That is fine for a smoke test and meaningless as a scientific result;
# do not quote these numbers anywhere.
# ---------------------------------------------------------------------------
def synthetic(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "orbital_period": rng.uniform(0.5, 500, n),
            "transit_duration": rng.uniform(0.5, 15, n),
            "planet_radius": rng.uniform(0.3, 20, n),
            "stellar_radius": rng.uniform(0.3, 3.0, n),
            "stellar_mass": rng.uniform(0.3, 2.0, n),
            "stellar_temp": rng.uniform(3000, 7500, n),
            "transit_depth": rng.uniform(10, 20000, n),
            "snr": rng.uniform(5, 200, n),
            "semi_major_axis": rng.uniform(0.01, 2.0, n),
            "equilibrium_temp": rng.uniform(100, 2500, n),
        }
    )
    df["disposition"] = np.where(
        (df["snr"] > 25) & (df["transit_depth"] > 200) & (df["planet_radius"] < 12),
        "CONFIRMED",
        np.where((df["snr"] > 10) & (df["planet_radius"] < 18), "CANDIDATE", "FALSE POSITIVE"),
    )
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description="Download KOI data from the NASA Exoplanet Archive")
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--limit", type=int, default=None, help="cap rows (omit for the full table)")
    ap.add_argument("--synthetic", action="store_true", help="write the offline fixture instead")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.synthetic:
        df = synthetic()
        path = out / "synthetic_train.csv"
        df.to_csv(path, index=False)
        print(f"[ingest] synthetic fixture: {len(df)} rows -> {path}")
        return

    try:
        df = fetch_koi(limit=args.limit)
        path = out / "koi_train.csv"
        df.to_csv(path, index=False)
        print(f"[ingest] NASA KOI: {len(df)} rows -> {path}")
        print(f"[ingest] class balance: {df['disposition'].value_counts().to_dict()}")
    except Exception as e:  # noqa: BLE001
        print(f"[ingest] NASA fetch failed ({e})")
        df = synthetic()
        path = out / "synthetic_train.csv"
        df.to_csv(path, index=False)
        print(f"[ingest] fell back to synthetic fixture: {len(df)} rows -> {path}")


if __name__ == "__main__":
    main()
