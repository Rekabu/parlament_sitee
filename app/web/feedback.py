from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Feedback, Idea, IdeaVote, User
from app.core.auth import get_current_user


router = APIRouter(tags=["feedback"])


@router.get("/feedback", response_class=HTMLResponse)
async def feedback_and_voting(
    request: Request,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    """Страница с голосованием за идеи и кнопкой перехода к форме."""
    
    # Получаем все идеи, сортируем по количеству голосов (сначала популярные)
    ideas = session.exec(select(Idea).order_by(Idea.votes_count.desc(), Idea.created_at.desc())).all()
    
    # Получаем список ID идей, за которые текущий пользователь уже проголосовал
    voted_idea_ids = []
    if user:
        votes = session.exec(select(IdeaVote).where(IdeaVote.user_id == user.id)).all()
        voted_idea_ids = [v.idea_id for v in votes]

    from app.main import render
    return render(
        request,
        "pages/feedback.html",
        {
            "title": "Ящик идей",
            "ideas": ideas,
            "voted_idea_ids": voted_idea_ids,
            "user": user
        },
    )


@router.post("/feedback/vote/{idea_id}")
async def vote_for_idea(
    idea_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    """Обработка голоса за идею."""
    if not user:
        # Если не залогинен, отправляем на вход
        return RedirectResponse(url="/auth/login", status_code=303)

    # Проверяем, не голосовал ли уже
    existing_vote = session.exec(
        select(IdeaVote).where(IdeaVote.idea_id == idea_id, IdeaVote.user_id == user.id)
    ).first()

    if not existing_vote:
        # Записываем голос
        new_vote = IdeaVote(idea_id=idea_id, user_id=user.id)
        session.add(new_vote)
        
        # Увеличиваем счетчик у идеи
        idea = session.get(Idea, idea_id)
        if idea:
            idea.votes_count += 1
            session.add(idea)
            
        session.commit()

    return RedirectResponse(url="/feedback", status_code=303)


@router.get("/feedback/form", response_class=HTMLResponse)
async def feedback_form(request: Request):
    """Показать форму обратной связи."""
    from app.main import render
    return render(
        request,
        "pages/feedback_form.html",
        {"title": "Написать нам"},
    )


@router.post("/feedback/form")
async def feedback_submit(
    request: Request,
    name: str = Form(""),
    class_name: str = Form(""),
    message: str = Form(...),
    is_anonymous: bool = Form(False),
    session: Session = Depends(get_session),
):
    """Обработать отправку сообщения."""
    fb = Feedback(
        name=None if is_anonymous else name,
        class_name=None if is_anonymous else class_name,
        message=message,
        is_anonymous=is_anonymous,
    )
    session.add(fb)
    session.commit()

    from app.main import render
    return render(
        request,
        "pages/feedback_form.html",
        {
            "title": "Написать нам",
            "success": "Спасибо! Ваше сообщение отправлено. Парламент скоро его прочитает.",
        },
    )