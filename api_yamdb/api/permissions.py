from rest_framework import permissions

from reviews.models import UserRole


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ к созданию и изменению объекта только у админа"""

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))

    def has_object_permission(self, request, view, obj):
        """Выполнение запроса на конкретном объекте."""
        return self.has_permission(request, view)


class IsAdmin(permissions.BasePermission):
    """Доступ ко всему только у админа"""

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        return request.user.is_authenticated and request.user.is_admin


class IsAdminModeratorAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Доступ к изменению объекта для админа, модератора и автора."""

    def has_object_permission(self, request, view, obj):
        """Выполнение запроса на конкретном объекте."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)
