from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator

from .constants import FORBIDDEN_USERNAMES


def validate_username(username: str) -> str:
    """Валидация имени пользователя."""

    UnicodeUsernameValidator()(username)

    if username in FORBIDDEN_USERNAMES:
        raise ValidationError(f'username не может быть {username}')

    return username
