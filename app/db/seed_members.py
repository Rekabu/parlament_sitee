from sqlmodel import Session, select
from app.db.session import engine
from app.models import Member, Committee


def seed_members():
    with Session(engine) as session:
        # Проверяем, есть ли уже данные
        if session.exec(select(Member)).first():
            print("Участники уже существуют, пропускаем")
            return

        # Создаём комитеты
        com_edu = Committee(name="Учебный комитет", description="Помощь в учёбе, олимпиады")
        com_sport = Committee(name="Спортивный комитет", description="Турниры и соревнования")
        
        session.add(com_edu)
        session.add(com_sport)
        session.commit()
        session.refresh(com_edu)
        session.refresh(com_sport)

        # Создаём участников
        members = [
            Member(
                first_name="Кирилл", last_name="Резвых",
                role="Председатель", class_name="10А",
                order_priority=1
            ),
            Member(
                first_name="Анна", last_name="Иванова",
                role="Заместитель председателя", class_name="11Б",
                order_priority=2
            ),
            Member(
                first_name="Дмитрий", last_name="Смирнов",
                role="Глава спортивного комитета", class_name="9В",
                committee_id=com_sport.id,
                order_priority=3
            ),
            Member(
                first_name="Елена", last_name="Петрова",
                role="Глава учебного комитета", class_name="10Б",
                committee_id=com_edu.id,
                order_priority=3
            ),
        ]

        for m in members:
            session.add(m)
        
        session.commit()
        print(f"Добавлено {len(members)} участников и 2 комитета.")


if __name__ == "__main__":
    seed_members()