from ai_service import generate_text


def answer_question(question: str) -> str:
    prompt = f"""
You are EduGenie, an educational assistant.

Answer the student's question accurately and concisely.
- Use simple language.
- Explain the key idea first.
- Add a short example when useful.
- If the question is ambiguous, state the assumption you are making.
- Do not invent citations or sources.

Student question:
{question}
""".strip()
    return generate_text(prompt, temperature=0.3, max_output_tokens=900)
