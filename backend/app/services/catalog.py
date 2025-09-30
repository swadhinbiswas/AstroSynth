"""Static mission catalogue (NASA Kepler / K2 / TESS)."""

MISSIONS = [
    {
        "id": "kepler",
        "name": "Kepler",
        "description": (
            "NASA's planet-hunting workhorse (2009-2018). Stared at 150k stars in Cygnus-Lyra, "
            "found 2,600+ confirmed exoplanets via transit photometry."
        ),
        "years": "2009–2018",
        "targets": 150000,
        "candidates": 9564,
    },
    {
        "id": "k2",
        "name": "K2",
        "description": (
            "Kepler's second life (2014-2018). Balanced on two reaction wheels, surveyed the ecliptic in 19 campaigns."
        ),
        "years": "2014–2018",
        "targets": 300000,
        "candidates": 4896,
    },
    {
        "id": "tess",
        "name": "TESS",
        "description": (
            "Transiting Exoplanet Survey Satellite (2018-). All-sky survey focused on "
            "bright nearby stars ideal for follow-up."
        ),
        "years": "2018–present",
        "targets": 200000,
        "candidates": 7000,
    },
]

DATASETS = [
    {
        "id": "kepler-koi-dr25",
        "mission": "kepler",
        "name": "Kepler KOI DR25",
        "rows": 9564,
        "version": "DR25",
        "url": "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=cumulative",
    },
    {
        "id": "k2-candidates",
        "mission": "k2",
        "name": "K2 Planet Candidates",
        "rows": 4896,
        "version": "v2024",
        "url": "https://exoplanetarchive.ipac.caltech.edu/",
    },
    {
        "id": "tess-toi",
        "mission": "tess",
        "name": "TESS TOI Catalog",
        "rows": 7000,
        "version": "2024.10",
        "url": "https://exoplanetarchive.ipac.caltech.edu/",
    },
]
