from datetime import datetime
from sqlmodel import SQLModel, Field


class News(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    summary: str = Field(default="")
    content: str = Field(default="")
    category: str = Field(default="Общее")
    
    author_id: int | None = Field(default=None, foreign_key="user.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)