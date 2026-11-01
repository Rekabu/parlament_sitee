from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.core.security import hash_password, verify_password
from app.db.session import get_session
from app.models import User, Role


router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"title": "Регистрация"},
    )


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    class_name: str = Form(""),
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"title": "Регистрация", "error": "Такой логин уже занят"},
        )

        # Создаём пользователя
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=Role.STUDENT,
        class_name=class_name or None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Сразу логиним
    request.session["user_id"] = user.id
    
    # Вместо главной кидаем на заполнение профиля!
    return RedirectResponse(url="/profile/setup", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"title": "Вход"},
    )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"title": "Вход", "error": "Неверный логин или пароль"},
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)