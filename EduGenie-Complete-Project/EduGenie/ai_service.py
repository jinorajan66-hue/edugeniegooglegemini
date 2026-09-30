from __future__ import annotations

from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel

from config import get_settings

T = TypeVar("T", bound=BaseModel)


class AIConfigurationError(RuntimeError):
    """Raised when Gemini is not configured."""


class AIServiceError(RuntimeError):
    """Raised when an AI request fails."""


@lru_cache
def get_gemini_client() -> Any:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise AIConfigurationError(
            "GEMINI_API_KEY is not configured. Add it to the .env file."
        )

    try:
        from google import genai
        return genai.Client(api_key=settings.gemini_api_key)
    except ImportError as exc:
        raise AIConfigurationError(
            "The google-genai package is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc
    except Exception as exc:
        raise AIConfigurationError(f"Could not initialize Gemini: {exc}") from exc


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.4,
    max_output_tokens: int = 1200,
) -> str:
    settings = get_settings()
    if settings.demo_mode:
        return (
            "Demo mode is enabled. Add a Gemini API key and set DEMO_MODE=false "
            "in .env to receive live AI-generated content."
        )

    try:
        from google.genai import types

        client = get_gemini_client()
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            raise AIServiceError("Gemini returned an empty response.")
        return text.strip()
    except (AIConfigurationError, AIServiceError):
        raise
    except ImportError as exc:
        raise AIConfigurationError(
            "The google-genai package is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc
    except Exception as exc:
        raise AIServiceError(f"Gemini request failed: {exc}") from exc


def generate_structured(
    prompt: str,
    response_model: type[T],
    *,
    temperature: float = 0.3,
    max_output_tokens: int = 1800,
) -> T:
    settings = get_settings()
    if settings.demo_mode:
        raise AIServiceError("Structured AI output is unavailable in demo mode.")

    try:
        from google.genai import types

        client = get_gemini_client()
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            raise AIServiceError("Gemini returned an empty structured response.")
        return response_model.model_validate_json(text)
    except (AIConfigurationError, AIServiceError):
        raise
    except ImportError as exc:
        raise AIConfigurationError(
            "The google-genai package is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc
    except Exception as exc:
        raise AIServiceError(f"Structured Gemini request failed: {exc}") from exc
