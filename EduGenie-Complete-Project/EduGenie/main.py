from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai_service import AIConfigurationError, AIServiceError
from config import get_settings
from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from schemas import (
    LearningPathResponse,
    QuestionRequest,
    QuizResponse,
    TextRequest,
    TopicRequest,
)
from summary_module import summarize_text

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Google Gemini powered educational assistant.",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "app_name": settings.app_name,
        },
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
        "local_explanation_enabled": settings.enable_local_explanation,
        "demo_mode": settings.demo_mode,
    }


def _handle_ai_error(exc: Exception):
    from fastapi import HTTPException

    if isinstance(exc, AIConfigurationError):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if isinstance(exc, AIServiceError):
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail="Unexpected server error.") from exc


@app.post("/qa")
async def qa(payload: QuestionRequest):
    try:
        return {"answer": answer_question(payload.question)}
    except Exception as exc:
        _handle_ai_error(exc)


@app.post("/explain")
async def explain(payload: TopicRequest):
    try:
        return {"explanation": explain_topic(payload.topic)}
    except Exception as exc:
        _handle_ai_error(exc)


@app.post("/quiz", response_model=QuizResponse)
async def quiz(payload: TextRequest):
    try:
        return generate_quiz(payload.text)
    except Exception as exc:
        _handle_ai_error(exc)


@app.post("/summarize")
async def summarize(payload: TextRequest):
    try:
        return {"summary": summarize_text(payload.text)}
    except Exception as exc:
        _handle_ai_error(exc)


@app.post("/learn/recommendations", response_model=LearningPathResponse)
async def learning_recommendations(payload: TopicRequest):
    try:
        return get_learning_recommendations(payload.topic)
    except Exception as exc:
        _handle_ai_error(exc)
