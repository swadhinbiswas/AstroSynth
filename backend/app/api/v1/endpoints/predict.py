from fastapi import APIRouter, Request

from app.core.rate_limit import rate_limit
from app.schemas import BatchPredictRequest, ExoplanetFeatures, PredictResponse
from app.services.predictor import MODEL_NAME, MODEL_VERSION, predict_proba
from app.services.shap_service import explain_local

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict(body: ExoplanetFeatures, request: Request):
    rate_limit(request)
    feats = body.model_dump()
    pred, conf, proba = predict_proba(feats)
    expl = explain_local(feats)
    return PredictResponse(
        predicted_class=pred,
        confidence=round(conf, 4),
        probabilities={k: round(float(v), 4) for k, v in proba.items()},
        explanations=expl,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
    )


@router.post("/batch-predict")
def batch_predict(body: BatchPredictRequest, request: Request):
    rate_limit(request, limit_per_minute=30)
    out = []
    for row in body.rows:
        feats = row.model_dump()
        pred, conf, proba = predict_proba(feats)
        out.append(
            {
                "predicted_class": pred,
                "confidence": round(conf, 4),
                "probabilities": proba,
                "input": feats,
            }
        )
    return {
        "count": len(out),
        "results": out,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
    }


@router.get("/model-info")
def model_info():
    from app.services.predictor import feature_importance_global

    return {
        "name": MODEL_NAME,
        "version": MODEL_VERSION,
        "algorithm": "RandomForestClassifier",
        "classes": ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"],
        "features": [
            "orbital_period",
            "transit_duration",
            "planet_radius",
            "stellar_radius",
            "stellar_mass",
            "stellar_temp",
            "transit_depth",
            "snr",
            "semi_major_axis",
            "equilibrium_temp",
        ],
        "feature_importance": feature_importance_global(),
    }
