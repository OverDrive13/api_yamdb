from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.core.exceptions import ValidationError


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Нельзя добавлять произведения, которые еще не вышли.'
        )


def validate_username(username):
    if username == 'me':
        raise ValidationError(
            'Недопустимое имя пользователя!'
        )


username_validator = UnicodeUsernameValidator()
