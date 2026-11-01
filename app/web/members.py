from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Member, Committee


router = APIRouter(tags=["members"])


@router.get("/members", response_class=HTMLResponse)
async def members_list(
    request: Request,
    session: Session = Depends(get_session),
):
    """Страница со списком участников парламента."""
    # Получаем всех участников, сортируем по приоритету (Председатель первый)
    members = session.exec(
        select(Member).order_by(Member.order_priority, Member.last_name)
    ).all()

    # Получаем все комитеты
    committees = session.exec(select(Committee)).all()

    from app.main import render
    return render(
        request,
        "pages/members.html",
        {
            "title": "Состав парламента",
            "members": members,
            "committees": committees,
        },
    )