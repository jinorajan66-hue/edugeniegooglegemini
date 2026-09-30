import pytest
from fastapi.testclient import TestClient

import main
from ai_service import AIConfigurationError


@pytest.fixture
def client():
    return TestClient(main.app)


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_qa_endpoint(client, monkeypatch):
    monkeypatch.setattr(main, "answer_question", lambda question: "The answer is 42.")
    response = client.post("/qa", json={"question": "What is the answer?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "The answer is 42."


def test_explain_endpoint(client, monkeypatch):
    monkeypatch.setattr(main, "explain_topic", lambda topic: "Simple explanation.")
    response = client.post("/explain", json={"topic": "Photosynthesis"})
    assert response.status_code == 200
    assert response.json()["explanation"] == "Simple explanation."


def test_quiz_endpoint(client, monkeypatch):
    from schemas import QuizResponse

    fake = QuizResponse(
        title="Test Quiz",
        questions=[
            {
                "question": "Q1?",
                "options": ["A", "B", "C", "D"],
                "answer_index": 1,
                "explanation": "B is correct.",
            },
            {
                "question": "Q2?",
                "options": ["A", "B", "C", "D"],
                "answer_index": 0,
                "explanation": "A is correct.",
            },
            {
                "question": "Q3?",
                "options": ["A", "B", "C", "D"],
                "answer_index": 3,
                "explanation": "D is correct.",
            },
        ],
    )
    monkeypatch.setattr(main, "generate_quiz", lambda text: fake)
    response = client.post("/quiz", json={"text": "Pythagoras theorem"})
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 3


def test_summary_endpoint(client, monkeypatch):
    monkeypatch.setattr(main, "summarize_text", lambda text: "Short summary.")
    response = client.post("/summarize", json={"text": "Long educational text."})
    assert response.status_code == 200
    assert response.json()["summary"] == "Short summary."


def test_learning_path_endpoint(client, monkeypatch):
    from schemas import LearningPathResponse

    fake = LearningPathResponse(
        topic="SQL",
        overview="Learn SQL step by step.",
        levels=[
            {"level": "Beginner", "duration": "1 week", "topics": ["SELECT"], "resources": ["Docs"]},
            {"level": "Intermediate", "duration": "2 weeks", "topics": ["JOIN"], "resources": ["Practice"]},
            {"level": "Advanced", "duration": "3 weeks", "topics": ["Indexes"], "resources": ["Projects"]},
        ],
        practice_projects=["Build an employee database"],
    )
    monkeypatch.setattr(main, "get_learning_recommendations", lambda topic: fake)
    response = client.post("/learn/recommendations", json={"topic": "SQL"})
    assert response.status_code == 200
    assert response.json()["topic"] == "SQL"


def test_ai_configuration_error_becomes_503(client, monkeypatch):
    def fail(_):
        raise AIConfigurationError("Missing key")

    monkeypatch.setattr(main, "answer_question", fail)
    response = client.post("/qa", json={"question": "Test"})
    assert response.status_code == 503
    assert "Missing key" in response.json()["detail"]
