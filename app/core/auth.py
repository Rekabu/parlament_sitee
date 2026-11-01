from fastapi import Request, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.models import User, Role


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User | None:
    """
    Возвращает текущего пользователя из сессии или None, если не залогинен.
    Не выбрасывает ошибку — используется там, где пользователь опционален.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = session.get(User, user_id)
    if not user:
        # Сессия есть, а пользователя нет (удалили из БД) — чистим сессию
        request.session.clear()
        return None

    return user


def require_user(
    user: User | None = Depends(get_current_user),
) -> User:
    """
    Требует залогиненного пользователя. Если нет — 401.
    Используется в защищённых роутах.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
        )
    return user


def require_role(*roles: Role):
    """
    Фабрика зависимостей для проверки роли.
    Пример: user: User = Depends(require_role(Role.ADMIN, Role.CHAIR))
    """
    def checker(user: User = Depends(require_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return user
    return checker