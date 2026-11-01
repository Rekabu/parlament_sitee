from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select  
from app.db.session import get_session
from app.core.auth import require_user
from app.models import User


router = APIRouter(tags=["profile"])


@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    user: User = Depends(require_user),
):
    from app.main import render
    return render(
        request,
        "auth/profile.html",
        {"title": "Профиль", "user": user}, 
    )

from fastapi import Form 
from fastapi.responses import RedirectResponse  

@router.get("/profile/setup", response_class=HTMLResponse)
async def profile_setup_form(
    request: Request,
    user: User = Depends(require_user),
):
    """Страница заполнения имени и фамилии после регистрации."""
    from app.main import render
    return render(
        request,
        "auth/profile_setup.html",
        {"title": "Завершение регистрации", "user": user},
    )


@router.post("/profile/setup")
async def profile_setup_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    class_name: str = Form(""),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    """Сохраняем имя и фамилию."""
    user.first_name = first_name
    user.last_name = last_name
    if class_name:
        user.class_name = class_name
        
    session.add(user)
    session.commit()
    
    return RedirectResponse(url="/", status_code=303)