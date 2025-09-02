from pydantic import BaseModel
from typing import List

class AskRequest(BaseModel):
    question: str
    session_id: str

class DocumentContext(BaseModel):
    page_content: str
    metadata: dict = {}

class AskResponse(BaseModel):
    answer: str
    context: List[DocumentContext] = []
