//models / question.py
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    conversation_id: str | None = None
