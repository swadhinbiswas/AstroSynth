from fastapi import APIRouter

from app.schemas import FeedbackRequest

router = APIRouter(tags=["feedback"])
_store: list[dict] = []


@router.post("/feedback")
def submit_feedback(body: FeedbackRequest):
    _store.append(body.model_dump())
    return {
        "ok": True,
        "total": len(_store),
        "message": "Thanks, explorer. Your label improves future training.",
    }


@router.get("/feedback")
def list_feedback():
    return {"count": len(_store), "items": _store[-50:]}
