from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .models import ErrorResponse, RecommendRequest, RecommendResponse
from .recommender import default_recommender
from .web import index_html

app = FastAPI(title="MoodMusic", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(index_html())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/recommend",
    response_model=RecommendResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def recommend(req: RecommendRequest) -> RecommendResponse:
    try:
        rec = default_recommender()
        hits = rec.recommend(req.mood_text, k=req.k)
        return RecommendResponse(model=rec.config.model_name, results=hits)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": str(e)})
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})


def main() -> None:
    import uvicorn

    uvicorn.run(
        "moodmusic.api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
