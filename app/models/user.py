from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field


class Role(str, Enum):
    STUDENT = "student" # Обычный ученик 
    MEMBER = "member" # Участник парламента 
    CHAIR = "chair" # Председатель 
    ADMIN = "admin" #Администатор 


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    
    # Новые поля (пока могут быть пустыми, заполним на втором шаге)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    
    role: Role = Field(default=Role.STUDENT)
    class_name: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)