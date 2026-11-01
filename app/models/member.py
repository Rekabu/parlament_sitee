from datetime import datetime
from sqlmodel import SQLModel, Field


class Committee(SQLModel, table=True):
    """Комитеты (например, учебный, спортивный)."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str | None = Field(default=None)


class Member(SQLModel, table=True):
    """Участник школьного парламента."""
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    role: str = Field(default="Член парламента")
    class_name: str | None = Field(default=None)
    
    # Поле для хранения имени файла с фото
    photo: str | None = Field(default=None)  
    
    # Связь с комитетом
    committee_id: int | None = Field(default=None, foreign_key="committee.id")
    
    order_priority: int = Field(default=10) 
    created_at: datetime = Field(default_factory=datetime.utcnow)