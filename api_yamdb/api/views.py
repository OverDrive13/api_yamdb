
=======
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins, filters

from reviews.models import Category, Genre, Title
from api.serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer)


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
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

    def perform_create(self, serializer):
        serializer.save(category=self.request.category,
                        genre=self.request.genre)
