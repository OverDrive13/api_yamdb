from django.db import models

MAX_LENGTH_NAME = 256

SCORES = (
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
    (8, 8), (9, 9), (10, 10)
)


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


class RelatedName():

    class Meta:
        default_related_name = '%(class)ss'


class Review(models.Model):
    text = models.TextField('Текст отзыва')
    author = models.IntegerField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField('Оценка', choices=SCORES)
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta(RelatedName.Meta):
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:10]} {self.author} {self.pub_date}'


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    author = models.IntegerField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta(RelatedName.Meta):
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.text[:10]} {self.author} {self.pub_date}'