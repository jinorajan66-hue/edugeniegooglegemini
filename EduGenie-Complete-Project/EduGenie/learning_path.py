from ai_service import generate_structured
from schemas import LearningPathResponse


def get_learning_recommendations(topic: str) -> LearningPathResponse:
    prompt = f"""
Create a personalized learning path for the topic: "{topic}".

Return exactly three levels:
- Beginner
- Intermediate
- Advanced

For each level provide:
- a realistic estimated duration,
- ordered topics to study,
- useful resource types or search suggestions.

Also provide a short overview and a few practice project ideas.
Keep the plan practical for a self-learner.
Return only the requested structured JSON object.
""".strip()

    result = generate_structured(
        prompt,
        LearningPathResponse,
        temperature=0.4,
        max_output_tokens=2200,
    )
    # The topic comes from the user's request, so preserve it in the UI even if
    # the model chooses a slightly different title.
    result.topic = topic
    return result
