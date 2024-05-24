from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import viewsets, mixins, filters, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination

from .permissions import (
    IsAuthenticatedOrOwnerReadOnly, IsAdmin, IsAdminModerator,
    IsAdminOrReadOnly
)
from reviews.models import (Category, Comment, Genre, Review,
                            Title, User, UserRole)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleResponseSerializer, TitleSerializer,
    UserSerializer, GetCodeSerializer, GetTokenSerializer
)


class CategoryViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Viewset для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (
        IsAdminOrReadOnly,
    )
    pagination_class = LimitOffsetPagination


class GenreViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Viewset для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (
        IsAdminOrReadOnly,
    )
    pagination_class = LimitOffsetPagination


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для модели Title."""
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return TitleSerializer
        return TitleResponseSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]
    permission_classes = (
        IsAuthenticatedOrOwnerReadOnly, permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    )
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrOwnerReadOnly, permissions.IsAuthenticatedOrReadOnly,
        IsAdmin, IsAdminModerator
    )
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    pagination_class = PageNumberPagination
    permission_classes = [IsAdmin]
    lookup_field = 'username'

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(IsAuthenticatedOrOwnerReadOnly,))
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
        return Response(
            data=request.data,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_confirmation_code(request):
    """Получить код подтверждения на указанный email"""
    serializer = GetCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    try:
        user, exist = User.objects.get_or_create(
            username=username,
            email=email,
            is_active=False
        )
    except Exception:
        return Response(request.data,
                        status=status.HTTP_400_BAD_REQUEST)
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
