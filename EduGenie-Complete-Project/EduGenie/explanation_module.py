from __future__ import annotations

from functools import lru_cache

from ai_service import AIServiceError, generate_text
from config import get_settings


@lru_cache
def _load_local_model():
    """Load LaMini only when explicitly enabled, avoiding a large startup download."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    settings = get_settings()
    tokenizer = AutoTokenizer.from_pretrained(settings.local_explanation_model)
    model = AutoModelForSeq2SeqLM.from_pretrained(settings.local_explanation_model)
    return tokenizer, model


def _explain_with_lamini(topic: str) -> str:
    tokenizer, model = _load_local_model()
    prompt = (
        "Explain the following educational topic for a beginner. "
        "Use simple language, a short definition, key points, and one example. "
        f"Topic: {topic}"
    )
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    output_ids = model.generate(
        **inputs,
        max_new_tokens=180,
        num_beams=4,
        early_stopping=True,
    )
    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()


def explain_topic(topic: str) -> str:
    settings = get_settings()

    if settings.enable_local_explanation:
        try:
            return _explain_with_lamini(topic)
        except Exception:
            # Keep the application usable if the optional local model cannot
            # be downloaded/loaded on the current machine.
            pass

    prompt = f"""
You are EduGenie, a beginner-friendly educational tutor.

Explain the topic "{topic}" in a way a school or college student can understand.
Use this structure:
1. Simple definition
2. How it works / main idea
3. 3 to 5 key points
4. One easy example
5. One-line recap

Avoid unnecessary jargon and do not invent facts.
""".strip()
    return generate_text(prompt, temperature=0.3, max_output_tokens=1000)
