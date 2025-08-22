from pydantic import BaseModel


class SummaryRequest(BaseModel):
    text: str
    api_key: str


class SummaryResponse(BaseModel):
    summary: str