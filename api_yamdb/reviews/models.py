from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .constants import MAX_LENGTH_NAME
from .validators import year_validator, validate_username


class UserRole(models.TextChoices):
    """Роли Юзера."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    @staticmethod
    def get_max_length():
        return max(len(role.value) for role in UserRole)


class User(AbstractUser):
    """Юзер."""

    username_validator = UnicodeUsernameValidator()
    bio = models.TextField(
        'Дополнительная информация о пользователе',
        blank=True,
    )
    username = models.CharField(validators=[username_validator,
                                validate_username],
                                max_length=MAX_LENGTH_NAME, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=MAX_LENGTH_NAME, blank=True)
    last_name = models.CharField(max_length=MAX_LENGTH_NAME, blank=True)
    confirmation_code = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=True)
    role = models.CharField(
        max_length=UserRole.get_max_length(),
        choices=UserRole.choices,
        default=UserRole.USER
    )
    objects = UserManager()

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN.value or self.is_superuser

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
        ordering = ('name',)
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
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class RelatedName:
    class Meta:
        default_related_name = '%(class)ss'


class Title(models.Model):
    """Произведения."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Жанр')
    year = models.SmallIntegerField(
        validators=[year_validator],
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre)
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание')

    class Meta(RelatedName.Meta):
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Отзыв."""

    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.SmallIntegerField(
        'Оценка',
        validators=[
            MaxValueValidator(10, ),
            MinValueValidator(1, )
        ]
    )
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta(RelatedName.Meta):
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.text[:10]} {self.author} {self.pub_date}'


class Comment(models.Model):
    """Комментарий."""

    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta(RelatedName.Meta):
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text[:10]} {self.author} {self.pub_date}'
