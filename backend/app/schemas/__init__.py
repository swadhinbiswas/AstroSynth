"""Pydantic v2 schemas for request/response validation."""

from typing import Literal

from pydantic import BaseModel, Field

Disposition = Literal["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
Mission = Literal["kepler", "k2", "tess"]


class ExoplanetFeatures(BaseModel):
    orbital_period: float = Field(..., gt=0, le=10000, description="Orbital period [days]")
    transit_duration: float = Field(..., gt=0, le=100, description="Transit duration [hours]")
    planet_radius: float = Field(..., gt=0, le=100, description="Planet radius [Earth radii]")
    stellar_radius: float = Field(..., gt=0, le=100, description="Stellar radius [Solar radii]")
    stellar_mass: float = Field(..., gt=0, le=10, description="Stellar mass [Solar masses]")
    stellar_temp: float = Field(..., gt=2000, le=12000, description="Stellar Teff [K]")
    transit_depth: float = Field(..., gt=0, description="Transit depth [ppm]")
    snr: float = Field(..., gt=0, le=10000, description="Signal-to-noise ratio")
    semi_major_axis: float = Field(..., gt=0, le=100, description="Semi-major axis [AU]")
    equilibrium_temp: float = Field(..., gt=0, le=5000, description="Equilibrium temp [K]")

    model_config = {"extra": "forbid"}


class PredictResponse(BaseModel):
    predicted_class: Disposition
    confidence: float
    probabilities: dict[str, float]
    explanations: dict
    model_name: str
    model_version: str


class BatchPredictRequest(BaseModel):
    rows: list[ExoplanetFeatures] = Field(..., min_length=1, max_length=1000)


class FeedbackRequest(BaseModel):
    prediction_id: str | None = None
    user_label: Disposition
    comment: str = Field(default="", max_length=2000)


class MissionInfo(BaseModel):
    id: Mission
    name: str
    description: str
    years: str
    targets: int
    candidates: int


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
