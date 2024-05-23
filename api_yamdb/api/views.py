from django.shortcuts import get_object_or_404, render

from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, action
from .permissions import IsAuthenticatedOrOwnerReadOnly, IsAdmin
from reviews.models import (Category, Comment, Genre, Review,
                            Title, User, UserRole)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, UserSerializer
)


class CategoryViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Viewset для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter, )


class GenreViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Viewset для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter, )


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для модели Title."""
    queryset = Title.objects.prefetch_related('reviews').all()
    serializer_class = TitleSerializer

    def perform_create(self, serializer):
        serializer.save(category=self.request.category,
                        genre=self.request.genre)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]

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
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']
    ]

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