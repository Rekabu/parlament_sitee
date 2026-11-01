from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


from app.core.config import settings

from app.admin import setup_admin


app = FastAPI(title="Школьный парламент Зыковской СОШ")
from fastapi.staticfiles import StaticFiles




app = FastAPI(title="Школьный парламент Зыковской СОШ")

# Подключаем статические файлы (CSS, картинки, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Middleware для сессий — подписанные cookie
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="parliament_session",
    max_age=14 * 24 * 60 * 60,  # 14 дней
    same_site="lax",
    https_only=False,
)

# Шаблоны
from sqlmodel import Session as SQLSession

from app.core.auth import get_current_user  # оставляем импорт, но не используем
from app.db.session import engine
from app.models import User


templates = Jinja2Templates(directory="app/templates")


def render(
    request: Request,
    template: str,
    context: dict | None = None,
    status_code: int = 200,
):
    """
    Обёртка над TemplateResponse: автоматически подставляет current_user.
    Достаёт User из БД по user_id из сессии.
    """
    context = context or {}

    current_user = None
    user_id = request.session.get("user_id")
    if user_id:
        with SQLSession(engine) as session:
            current_user = session.get(User, user_id)
            if not current_user:
                # Сессия устарела — пользователя нет в БД
                request.session.clear()

    context["request"] = request
    context["current_user"] = current_user

    return templates.TemplateResponse(
        request=request,
        name=template,
        context=context,
        status_code=status_code,
    )

# Роутеры

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render(request, "pages/home.html", {"title": "Главная"})


@app.get("/health")
async def health():
    return {"status": "ok"}



# Подключаем админку
setup_admin(app)

from app.web import auth as auth_router
from app.web import profile as profile_router
from app.web import about as about_router
from app.web import members as members_router
from app.web import feedback as feedback_router
from app.web import news as news_router

app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(about_router.router)
app.include_router(members_router.router)
app.include_router(feedback_router.router)
app.include_router(news_router.router)