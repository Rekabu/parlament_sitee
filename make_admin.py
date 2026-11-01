from sqlmodel import Session, select
from app.db.session import engine
from app.models import User, Role

def make_admin(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"Пользователь {username} не найден!")
            return
        
        user.role = Role.ADMIN
        session.add(user)
        session.commit()
        print(f"Пользователь {username} теперь АДМИНИСТРАТОР.")

if __name__ == "__main__":
    make_admin("Пипи")  # Впиши свой точный логин (как в профиле)