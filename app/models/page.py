from datetime import datetime

from sqlmodel import SQLModel, Field


class Page(SQLModel, table=True):
    """
    Статическая страница сайта.
    slug — короткое имя для URL (например, "about" → /about).
    content_md — содержимое в Markdown.
    """
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    title: str
    content_md: str = Field(default="")
    updated_at: datetime = Field(default_factory=datetime.utcnow)