from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import (Category, Comment, Genre, Review,
                            SCORES, Title, User, UserRole)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
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
        duplicated_username = User.objects.filter(
            username=username
        ).exists()
        if duplicated_username:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        return username

    def validate_email(self, email):
        duplicated_email = User.objects.filter(email=email).exists()
        if duplicated_email:
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )
        return email


class GetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z', max_length=150)

    def validate_username(self, username):
        return UserSerializer.validate_username(self, username)

    def validate_email(self, email):
        return UserSerializer.validate_email(self, email)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)