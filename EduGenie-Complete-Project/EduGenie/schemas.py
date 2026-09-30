from typing import Literal
from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)


class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=1000)


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(..., min_length=4, max_length=4)
    answer_index: int = Field(..., ge=0, le=3)
    explanation: str


class QuizResponse(BaseModel):
    title: str
    questions: list[QuizQuestion] = Field(..., min_length=3, max_length=3)


class LearningLevel(BaseModel):
    level: Literal["Beginner", "Intermediate", "Advanced"]
    duration: str
    topics: list[str]
    resources: list[str]


class LearningPathResponse(BaseModel):
    topic: str
    overview: str
    levels: list[LearningLevel] = Field(..., min_length=3, max_length=3)
    practice_projects: list[str] = Field(default_factory=list)
