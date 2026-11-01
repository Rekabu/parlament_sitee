from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Page
from app.utils.markdown import render_markdown


router = APIRouter(tags=["pages"])


@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    session: Session = Depends(get_session),
):
    """Страница «О парламенте». Контент из БД по slug='about'."""
    page = session.exec(select(Page).where(Page.slug == "about")).first()
    if not page:
        raise HTTPException(status_code=404, detail="Страница не найдена")

    from app.main import render

    return render(
        request,
        "pages/about.html",
        {
            "title": page.title,
            "page": page,
            "content_html": render_markdown(page.content_md),
        },
    )