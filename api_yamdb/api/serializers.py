from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Comment, Review, SCORES, Title


def get_rating(self, obj):
    """
    Метод для вычисления рейтинга для TitleSerializer:
    rating = serializers.SerializerMethodField()
    Также нужно во вью-сете TitleViewSet сделать
    prefetch_related в кверисете:
    queryset = Title.objects.prefetch_related('reviews').all()
    """
    scores = []
    for review in obj.reviews.all():
        scores.append(review.score)
    return round(sum(scores) / len(scores))


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.ChoiceField(choices=SCORES)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['author', 'title'],
                message='Пользователь может оставить только'
                        'один отзыв на произведение'
            ),
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)
