from django.contrib.auth import get_user_model
from django.db import models


SCORES = (
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
    (8, 8), (9, 9), (10, 10)
)

User = get_user_model()


class RelatedName():

    class Meta:
        default_related_name = '%(class)ss'


class Title(models.Model):
    pass


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
