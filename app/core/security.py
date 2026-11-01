import hashlib
import secrets


def hash_password(password: str) -> str:
    """
    Хеширует пароль с солью через PBKDF2-HMAC-SHA256.
    Возвращает строку в формате: salt$hash
    """
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,  # количество итераций
    )
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    Проверяет пароль против сохранённого хеша.
    Возвращает True, если пароль совпадает.
    """
    try:
        salt, hash_hex = stored.split("$", 1)
    except ValueError:
        return False

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return secrets.compare_digest(pwd_hash.hex(), hash_hex)