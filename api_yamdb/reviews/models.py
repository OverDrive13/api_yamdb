from enum import Enum

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from django.db import models

MAX_LENGTH_NAME = 256

SCORES = (
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
    (8, 8), (9, 9), (10, 10)
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user


class UserRole(Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    @staticmethod
    def get_max_length():
        max_length = max(len(role.value) for role in UserRole)
        return max_length

    @staticmethod
    def get_all_roles():
        return tuple((role.value, role.name) for role in UserRole)


class User(AbstractUser):
    USERNAME_VALIDATOR = RegexValidator(r'^[\w.@+-]+\Z')
    bio = models.TextField(
        'Дополнительная информация о пользователе',
        blank=True,
    )
    username = models.CharField(validators=[USERNAME_VALIDATOR],
                                max_length=150, unique=True)
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    password = models.CharField(blank=True, max_length=124)
    confirmation_code = models.CharField(max_length=60, default='000000')
    role = models.CharField(
        max_length=UserRole.get_max_length(),
        choices=UserRole.get_all_roles(),
        default=UserRole.USER.value
    )
    objects = CustomUserManager()

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Категория."""

    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            verbose_name='Категория')
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг')

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Genre(models.Model):
    """Жанр."""

    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            verbose_name='Жанр')
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения."""

    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            verbose_name='Жанр')
    year = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание')

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class RelatedName():
    class Meta:
        default_related_name = '%(class)ss'


class Review(models.Model):
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField('Оценка', choices=SCORES)
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta(RelatedName.Meta):
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:10]} {self.author} {self.pub_date}'


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta(RelatedName.Meta):
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.text[:10]} {self.author} {self.pub_date}'
