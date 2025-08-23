from pydantic import BaseModel, HttpUrl

# Input schema
class url(BaseModel):
    url: HttpUrl

# Output schema
class summ(BaseModel):
    summary: str
    source: str   # "transcript", "metadata", "web", or "none"
