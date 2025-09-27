"""Feature engineering: imputation, outlier clipping, derived physics features, scaling metadata."""
import numpy as np
import pandas as pd

FEATURES = [
    "orbital_period", "transit_duration", "planet_radius", "stellar_radius",
    "stellar_mass", "stellar_temp", "transit_depth", "snr",
    "semi_major_axis", "equilibrium_temp",
]
TARGET = "disposition"

# Plausible physical bounds (clip outliers instead of dropping science data)
BOUNDS = {
    "orbital_period": (0.2, 2000), "transit_duration": (0.2, 30),
    "planet_radius": (0.2, 30), "stellar_radius": (0.1, 10),
    "stellar_mass": (0.08, 5), "stellar_temp": (2500, 10000),
    "transit_depth": (1, 100000), "snr": (0.5, 5000),
    "semi_major_axis": (0.005, 10), "equilibrium_temp": (50, 4000),
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col, (lo, hi) in BOUNDS.items():
        if col in df.columns:
            df[col] = df[col].clip(lo, hi)
    # Median imputation (fit on train in production; median-of-frame here for simplicity)
    for col in FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    return df


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Add physics-motivated derived features."""
    df = clean(df)
    df = df.copy()
    df["snr_per_depth"] = df["snr"] / (df["transit_depth"] + 1)
    df["log_period"] = np.log1p(df["orbital_period"])
    df["radius_ratio"] = df["planet_radius"] / (df["stellar_radius"] * 109.2 + 1e-6)
    df["temp_ratio"] = df["equilibrium_temp"] / (df["stellar_temp"] + 1e-6)
    return df


def all_features() -> list[str]:
    return FEATURES + ["snr_per_depth", "log_period", "radius_ratio", "temp_ratio"]
