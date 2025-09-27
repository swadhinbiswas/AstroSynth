def test_engineer_adds_features():
    import pandas as pd
    from src.features import engineer
    df = pd.DataFrame([{
        "orbital_period": 10, "transit_duration": 3, "planet_radius": 2,
        "stellar_radius": 1, "stellar_mass": 1, "stellar_temp": 5778,
        "transit_depth": 1000, "snr": 30, "semi_major_axis": 0.1, "equilibrium_temp": 700,
    }])
    out = engineer(df)
    for c in ["snr_per_depth", "log_period", "radius_ratio", "temp_ratio"]:
        assert c in out.columns


def test_clean_clips_outliers():
    import pandas as pd
    from src.features import clean
    df = pd.DataFrame([{"orbital_period": 1e9, "transit_duration": 3, "planet_radius": 2, "stellar_radius": 1, "stellar_mass": 1, "stellar_temp": 5778, "transit_depth": 1000, "snr": 30, "semi_major_axis": 0.1, "equilibrium_temp": 700}])
    assert clean(df)["orbital_period"].iloc[0] <= 2000
