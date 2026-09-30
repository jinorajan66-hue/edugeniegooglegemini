from ai_service import generate_structured
from schemas import QuizResponse


def generate_quiz(text: str) -> QuizResponse:
    prompt = f"""
Create exactly 3 multiple-choice questions from the educational text below.

Requirements:
1. Each question must have exactly 4 options.
2. Use plausible distractors.
3. answer_index must be the zero-based index of the correct option.
4. Include a short explanation of the correct answer.
5. Questions must be answerable from the supplied text.
6. Return only the requested structured JSON object.

Educational text:
{text}
""".strip()
    return generate_structured(
        prompt,
        QuizResponse,
        temperature=0.25,
        max_output_tokens=1800,
    )
