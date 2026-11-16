from datetime import datetime

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    __tablename__ = "calendar_event"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str = Field(default="")
    location: str = Field(default="")
    starts_at: datetime = Field(index=True)
    ends_at: datetime | None = Field(default=None)
    all_day: bool = Field(default=False)
