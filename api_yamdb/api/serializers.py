import datetime as dt

from rest_framework import serializers

from reviews.constants import MAX_LENGTH_NAME, MAX_LENGTH_USER
from reviews.models import (
    Category, Comment, Genre, Review, Title, User, UserRole
)
from reviews.validators import (
    validate_username, validate_email, validate_username_exists)
from reviews.constants import USERNAME_VALIDATOR


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleResponseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        scores = []
        for review in obj.reviews.all():
            scores.append(review.score)
        if scores:
            return round(sum(scores) / len(scores))
        return None


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        if value > dt.date.today().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='id', read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'text', 'score', 'pub_date', 'title')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
        read_only_fields = ('review',)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[USERNAME_VALIDATOR,
                    validate_username, validate_username_exists],
        max_length=MAX_LENGTH_USER)
    first_name = serializers.CharField(
        max_length=MAX_LENGTH_USER, required=False)
    last_name = serializers.CharField(
        max_length=MAX_LENGTH_USER, required=False)
    email = serializers.CharField(validators=[validate_email],
                                  max_length=MAX_LENGTH_NAME)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        default=UserRole.USER,
        required=False
    )

    class Meta:
        fields = (
            'username',
            'first_name',
            'last_name',
            'bio',
            'role',
            'email'
        )
        model = User


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(validators=[USERNAME_VALIDATOR,
                                                 validate_username],
                                     required=True)
    confirmation_code = serializers.CharField(required=True)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=MAX_LENGTH_NAME, required=True)
    username = serializers.CharField(validators=[USERNAME_VALIDATOR,
                                                 validate_username],
                                     max_length=MAX_LENGTH_USER)
