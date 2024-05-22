from django.db import models

MAX_LENGTH_NAME = 256


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
    genre = models.ManyToManyField(Genre)
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
