from django.utils import timezone

from django.core.exceptions import ValidationError


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Введите корректный год!'
        )


def validate_username(username):
    if username == 'me':
        raise ValidationError(
            'Недопустимое имя пользователя!'
        )


def validate_email(email):
    from .models import User
    if User.objects.filter(email=email).exists():
        raise ValidationError(
            'Пользователь с таким email уже зарегистрирован'
        )
    return email


def validate_username_exists(username):
    from .models import User
    if User.objects.filter(username=username).exists():
        raise ValidationError(
            'Пользователь с таким именем уже зарегистрирован'
        )
    return username
