from ai_service import generate_text


def summarize_text(text: str) -> str:
    prompt = f"""
You are EduGenie, a study assistant.

Summarize the following educational passage for quick revision.
Keep the important facts, definitions, relationships, and conclusions.
Use clear headings or bullet points when helpful.
Do not add facts that are not supported by the passage.

Passage:
{text}
""".strip()
    return generate_text(prompt, temperature=0.2, max_output_tokens=1000)
