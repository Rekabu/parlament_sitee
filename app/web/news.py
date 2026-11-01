from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import News
from app.utils.markdown import render_markdown


router = APIRouter(tags=["news"])


@router.get("/news", response_class=HTMLResponse)
async def news_list(
    request: Request,
    session: Session = Depends(get_session),
):
    """Страница со списком всех новостей (с полным текстом)."""
    # Получаем все новости, сортируем от новых к старым
    news_items = session.exec(
        select(News).order_by(News.created_at.desc())
    ).all()

    # Для каждой новости сразу рендерим Markdown в HTML
    news_data = []
    for item in news_items:
        news_data.append({
            "item": item,
            "content_html": render_markdown(item.content)
        })

    from app.main import render
    return render(
        request,
        "pages/news_list.html",
        {"title": "Новости", "news_data": news_data},
    )


@router.get("/news/{news_id}", response_class=HTMLResponse)
async def news_detail(
    news_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """Страница отдельной новости (если на неё перейдут по прямой ссылке)."""
    news_item = session.get(News, news_id)
    if not news_item:
        raise HTTPException(status_code=404, detail="Новость не найдена")

    content_html = render_markdown(news_item.content)

    from app.main import render
    return render(
        request,
        "pages/news_detail.html",
        {
            "title": news_item.title,
            "news": news_item,
            "content_html": content_html,
        },
    )