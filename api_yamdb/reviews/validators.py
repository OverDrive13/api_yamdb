from django.utils import timezone

from django.core.exceptions import ValidationError


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Введите корректный год!'
        )


def validate_username(self, username):
    if username == 'me':
        raise ValidationError(
            'Недопустимое имя пользователя!'
        )
