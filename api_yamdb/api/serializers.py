import datetime as dt

from rest_framework import serializers

from reviews.constants import MAX_LENGTH_NAME
from reviews.models import (
    Category, Comment, Genre, Review, Title, User, UserRole
)


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
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z', max_length=150)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.CharField(max_length=254)
    role = serializers.ChoiceField(
        choices=UserRole.get_all_roles(),
        default=UserRole.USER.value,
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

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя!'
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )
        return email


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=MAX_LENGTH_NAME, required=True)
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z', max_length=150)

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя!')
        return username
