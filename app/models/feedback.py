from datetime import datetime
from sqlmodel import SQLModel, Field


class Feedback(SQLModel, table=True):
    """Сообщение из формы обратной связи."""
    id: int | None = Field(default=None, primary_key=True)
    
    # Данные отправителя (могут быть пустыми, если анонимно)
    name: str | None = Field(default=None)
    class_name: str | None = Field(default=None)
    email: str | None = Field(default=None)  # Для ответа
    
    # Само сообщение
    message: str
    is_anonymous: bool = Field(default=False)
    
    # Статус обработки
    status: str = Field(default="new")  # new, read, answered
    answer: str | None = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)