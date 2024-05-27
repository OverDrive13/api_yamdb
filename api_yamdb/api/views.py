from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from rest_framework import (
    viewsets, mixins, filters, permissions, status, serializers
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination

from .permissions import (
    IsAdmin, IsAdminModeratorAuthorOrReadOnly, IsAdminOrReadOnly)
from reviews.models import (
    Category, Comment, Genre, Review, Title, User, UserRole)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleResponseSerializer, TitleSerializer,
    UserSerializer, GetTokenSerializer, SignupSerializer
)
from .mixins import ModelMixinSet
from api.filters import TitleFilter


class CategoryViewSet(ModelMixinSet):
    """Viewset для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (
        IsAdminOrReadOnly,
    )
    lookup_field = 'slug'
    search_fields = ('name',)


class GenreViewSet(ModelMixinSet):
    """Viewset для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для модели Title."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year')
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return TitleSerializer
        return TitleResponseSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset для модели Review."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        user = self.request.user
        title_id = self.kwargs['title_id']
        if user.reviews.filter(title__id=title_id).exists():
            raise serializers.ValidationError(
                'Пользователь может оставить только один отзыв на произведение'
            )
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset для модели Comment."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]

    def get_review(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id, title__id=title_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    pagination_class = PageNumberPagination
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            user = self.request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status.HTTP_200_OK)

        if request.method == 'PATCH':
            user = get_object_or_404(User, id=request.user.id)
            fixed_data = self.request.data.copy()
            if ('role' in self.request.data
                    and user.role == UserRole.USER.value):
                fixed_data['role'] = UserRole.USER.value
            serializer = UserSerializer(
                user,
                data=fixed_data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return get_confirmation_code(request)


def get_confirmation_code(request):
    """Получить код подтверждения на указанный email"""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    try:
        user, _ = User.objects.get_or_create(username=username, email=email)
    except Exception:
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    User.objects.filter(username=username).update(
        confirmation_code=confirmation_code
    )
    subject = 'Регистрация на YAMDB'
    message = f'Код подтверждения: {confirmation_code}'
    send_mail(subject, message, 'YAMDB', [email])
    return Response(
        request.data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получить токен для работы с API по коду подтверждения"""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if confirmation_code == user.confirmation_code:
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)
