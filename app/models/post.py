from datetime import datetime
from pydantic import BaseModel


class PostCreate(BaseModel):
    content: str


class PostResponse(BaseModel):
    id: str
    author_id: str
    content: str
    likes_count: int
    created_at: datetime
