from datetime import datetime
from sqlmodel import SQLModel, Field


class Idea(SQLModel, table=True):
    """Идея, предложенная учеником."""
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    votes_count: int = Field(default=0)  # Счетчик лайков для быстрой сортировки
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IdeaVote(SQLModel, table=True):
    """Голос за идею (чтобы один пользователь не мог голосовать дважды)."""
    id: int | None = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)