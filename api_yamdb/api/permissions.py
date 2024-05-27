from rest_framework import permissions

from reviews.models import UserRole


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ к созданию и изменению объекта только у админа"""

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            is_admin = request.user.role == UserRole.ADMIN.value
            return is_admin or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """Выполнение запроса на конкретном объекте."""
        return self.has_permission(request, view)


class IsAdmin(permissions.BasePermission):
    """Доступ ко всему только у админа"""

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        if request.user.is_authenticated:
            is_admin = request.user.role == UserRole.ADMIN.value
            return is_admin or request.user.is_superuser


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Доступ к изменению объекта для админа, модератора и автора."""

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Выполнение запроса на конкретном объекте."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == UserRole.ADMIN.value
                or request.user.role == UserRole.MODERATOR.value
                or obj.author == request.user)
