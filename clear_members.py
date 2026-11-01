from sqlmodel import Session, select
from app.db.session import engine
from app.models import Member, Committee

def clear_members():
    with Session(engine) as session:
        # Удаляем всех участников
        members = session.exec(select(Member)).all()
        for m in members:
            session.delete(m)
        
        # Удаляем все комитеты
        committees = session.exec(select(Committee)).all()
        for c in committees:
            session.delete(c)
            
        session.commit()
        print(f"Удалено участников: {len(members)}, комитетов: {len(committees)}")

if __name__ == "__main__":
    clear_members()