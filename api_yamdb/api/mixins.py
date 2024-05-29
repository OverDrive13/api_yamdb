from rest_framework import filters
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet

from .permissions import IsAdminOrReadOnly


class ModelMixinSet(CreateModelMixin, ListModelMixin,
                    DestroyModelMixin, GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    permission_classes = (
        IsAdminOrReadOnly,
    )
    lookup_field = 'slug'
    search_fields = ('name',)
