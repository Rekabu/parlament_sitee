from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqladmin.i18n import I18nConfig
from starlette.requests import Request
from wtforms import SelectField
from app.db.session import engine
from app.models import User, Page, News, Member, Committee, Feedback, Idea, IdeaVote, Event
from app.core.config import settings
from sqlmodel import Session, select


class UserAdmin(ModelView, model=User):
    # Добавили first_name и last_name
    column_list = [User.id, User.username, User.first_name, User.last_name, User.role, User.class_name]
    column_labels = {
        User.id: "ID",
        User.username: "Логин",
        User.password_hash: "Хэш пароля",
        User.first_name: "Имя",
        User.last_name: "Фамилия",
        User.role: "Роль",
        User.class_name: "Класс",
        User.created_at: "Дата регистрации",
    }
    column_searchable_list = [User.username, User.first_name, User.last_name]
    column_formatters = {User.role: lambda model, _: _user_role_label(model.role)}
    column_formatters_detail = {User.role: lambda model, _: _user_role_label(model.role)}
    form_overrides = {"role": SelectField}
    form_args = {
        "role": {
            "choices": [
                ("STUDENT", "Ученик"),
                ("MEMBER", "Член парламента"),
                ("CHAIR", "Председатель"),
                ("ADMIN", "Администратор"),
            ],
        },
    }
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class PageAdmin(ModelView, model=Page):
    column_list = [Page.slug, Page.title, Page.updated_at]
    column_labels = {
        Page.slug: "Адрес страницы",
        Page.title: "Заголовок",
        Page.content_md: "Содержание",
        Page.updated_at: "Обновлено",
    }
    column_searchable_list = [Page.slug, Page.title]
    name = "Страница"
    name_plural = "Страницы"
    icon = "fa-solid fa-file-lines"


class NewsAdmin(ModelView, model=News):
    column_list = [News.id, News.title, News.category, News.created_at]
    column_labels = {
        News.id: "ID",
        News.title: "Заголовок",
        News.summary: "Краткое описание",
        News.content: "Текст новости",
        News.category: "Категория",
        News.author_id: "Автор",
        News.created_at: "Дата публикации",
    }
    column_searchable_list = [News.title, News.category]
    name = "Новость"
    name_plural = "Новости"
    icon = "fa-solid fa-newspaper"
    
class CommitteeAdmin(ModelView, model=Committee):
    column_list = [Committee.id, Committee.name]
    column_labels = {
        Committee.id: "ID",
        Committee.name: "Название",
        Committee.description: "Описание",
    }
    name = "Комитет"
    name_plural = "Комитеты"
    icon = "fa-solid fa-sitemap"


class MemberAdmin(ModelView, model=Member):
    column_list = [Member.id, Member.last_name, Member.first_name, Member.role, Member.class_name]
    column_labels = {
        Member.id: "ID",
        Member.first_name: "Имя",
        Member.last_name: "Фамилия",
        Member.role: "Должность",
        Member.class_name: "Класс",
        Member.photo: "Фотография",
        Member.committee_id: "Комитет",
        Member.order_priority: "Порядок отображения",
        Member.created_at: "Дата добавления",
    }
    column_searchable_list = [Member.last_name, Member.first_name]
    name = "Участник"
    name_plural = "Состав парламента"
    icon = "fa-solid fa-users"
    

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        # Проверяем пользователя в БД
        with Session(engine) as session:
            from app.core.security import verify_password
            from app.models import Role # Импортируем Role
            
            user = session.exec(select(User).where(User.username == username)).first()
            
            # user.role может быть строкой или Enum. Приводим к строке для надежности.
            user_role_str = str(user.role.value) if user and hasattr(user.role, 'value') else str(user.role if user else "")
            
            if user and verify_password(password, user.password_hash) and user_role_str == "admin":
                # Сохраняем в сессию ID пользователя
                request.session.update({"admin_user_id": user.id, "user_id": user.id})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Проверяем, есть ли user_id в сессии (общая сессия сайта)
        user_id = request.session.get("user_id")
        
        if user_id:
            with Session(engine) as session:
                user = session.get(User, user_id)
                # Приводим роль к строке
                user_role_str = str(user.role.value) if user and hasattr(user.role, 'value') else str(user.role if user else "")
                
                if user and user_role_str == "admin":
                    return True
                    
        return False

class FeedbackAdmin(ModelView, model=Feedback):
    column_list = [Feedback.id, Feedback.name, Feedback.class_name, Feedback.message, Feedback.status, Feedback.created_at]
    column_labels = {
        Feedback.id: "ID",
        Feedback.name: "Имя",
        Feedback.class_name: "Класс",
        Feedback.email: "Электронная почта",
        Feedback.message: "Сообщение",
        Feedback.is_anonymous: "Анонимно",
        Feedback.status: "Статус",
        Feedback.answer: "Ответ",
        Feedback.created_at: "Дата отправки",
    }
    column_searchable_list = [Feedback.name, Feedback.message]
    column_formatters = {
        Feedback.status: lambda model, _: _feedback_status_label(model.status),
    }
    column_formatters_detail = {
        Feedback.status: lambda model, _: _feedback_status_label(model.status),
    }
    form_overrides = {"status": SelectField}
    form_args = {
        "status": {
            "choices": [
                ("new", "Новое"),
                ("read", "Прочитано"),
                ("answered", "Отвечено"),
            ],
        },
    }
    name = "Сообщение"
    name_plural = "Обратная связь"
    icon = "fa-solid fa-envelope"
    
class IdeaAdmin(ModelView, model=Idea):
    column_list = [Idea.id, Idea.title, Idea.votes_count, Idea.created_at]
    column_labels = {
        Idea.id: "ID",
        Idea.title: "Заголовок",
        Idea.description: "Описание",
        Idea.votes_count: "Голоса",
        Idea.created_at: "Дата создания",
    }
    column_searchable_list = [Idea.title]
    name = "Идея"
    name_plural = "Идеи"
    icon = "fa-solid fa-lightbulb"


class EventAdmin(ModelView, model=Event):
    column_list = [Event.title, Event.starts_at, Event.ends_at, Event.location, Event.all_day]
    column_labels = {
        Event.id: "ID",
        Event.title: "Название",
        Event.description: "Описание",
        Event.location: "Место проведения",
        Event.starts_at: "Начало",
        Event.ends_at: "Окончание",
        Event.all_day: "Весь день",
    }
    column_searchable_list = [Event.title, Event.location]
    form_columns = [
        Event.title,
        Event.description,
        Event.location,
        Event.starts_at,
        Event.ends_at,
        Event.all_day,
    ]
    name = "Мероприятие"
    name_plural = "Мероприятия"
    icon = "fa-solid fa-calendar-days"


def _user_role_label(role: object) -> str:
    value = getattr(role, "value", role)
    return {
        "student": "Ученик",
        "member": "Член парламента",
        "chair": "Председатель",
        "admin": "Администратор",
    }.get(str(value), str(value))


def _feedback_status_label(status: str) -> str:
    return {
        "new": "Новое",
        "read": "Прочитано",
        "answered": "Отвечено",
    }.get(status, status)


def setup_admin(app):
    authentication_backend = AdminAuth(secret_key=settings.secret_key)
    
    admin = Admin(
        app, 
        engine, 
        title="Админ-панель Парламента",
        authentication_backend=authentication_backend,
        templates_dir="templates_admin",
        i18n_config=I18nConfig(
            default_locale="ru",
            language_cookie_name=None,
            language_header_name=None,
        ),
    )
    admin.add_view(UserAdmin)
    admin.add_view(PageAdmin)
    admin.add_view(NewsAdmin)
    admin.add_view(CommitteeAdmin)  
    admin.add_view(MemberAdmin)    
    admin.add_view(FeedbackAdmin)
    admin.add_view(IdeaAdmin)
    admin.add_view(EventAdmin)
    