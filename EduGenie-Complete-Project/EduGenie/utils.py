import json
import re
from typing import Any


def clean_json_block(text: str) -> str:
    """Remove Markdown fences and surrounding whitespace from a JSON response."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def parse_json(text: str) -> Any:
    """Parse JSON after removing common Markdown formatting."""
    return json.loads(clean_json_block(text))
