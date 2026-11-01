from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.db.session import engine
from app.models import User, Page, News, Member, Committee, Feedback, Idea, IdeaVote
from app.core.config import settings
from sqlmodel import Session, select


class UserAdmin(ModelView, model=User):
    # Добавили first_name и last_name
    column_list = [User.id, User.username, User.first_name, User.last_name, User.role, User.class_name]
    column_searchable_list = [User.username, User.first_name, User.last_name]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class PageAdmin(ModelView, model=Page):
    column_list = [Page.slug, Page.title, Page.updated_at]
    column_searchable_list = [Page.slug, Page.title]
    name = "Страница"
    name_plural = "Страницы"
    icon = "fa-solid fa-file-lines"


class NewsAdmin(ModelView, model=News):
    column_list = [News.id, News.title, News.category, News.created_at]
    column_searchable_list = [News.title, News.category]
    name = "Новость"
    name_plural = "Новости"
    icon = "fa-solid fa-newspaper"
    
class CommitteeAdmin(ModelView, model=Committee):
    column_list = [Committee.id, Committee.name]
    name = "Комитет"
    name_plural = "Комитеты"
    icon = "fa-solid fa-sitemap"


class MemberAdmin(ModelView, model=Member):
    column_list = [Member.id, Member.last_name, Member.first_name, Member.role, Member.class_name]
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
    column_searchable_list = [Feedback.name, Feedback.message]
    name = "Сообщение"
    name_plural = "Обратная связь"
    icon = "fa-solid fa-envelope"
    
class IdeaAdmin(ModelView, model=Idea):
    column_list = [Idea.id, Idea.title, Idea.votes_count, Idea.created_at]
    column_searchable_list = [Idea.title]
    name = "Идея"
    name_plural = "Идеи"
    icon = "fa-solid fa-lightbulb"

def setup_admin(app):
    authentication_backend = AdminAuth(secret_key=settings.secret_key)
    
    admin = Admin(
        app, 
        engine, 
        title="Админ-панель Парламента",
        authentication_backend=authentication_backend,
        templates_dir="templates_admin"
    )
    admin.add_view(UserAdmin)
    admin.add_view(PageAdmin)
    admin.add_view(NewsAdmin)
    admin.add_view(CommitteeAdmin)  
    admin.add_view(MemberAdmin)    
    admin.add_view(FeedbackAdmin)
    admin.add_view(IdeaAdmin)
    