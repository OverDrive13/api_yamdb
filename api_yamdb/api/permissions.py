from rest_framework import permissions

from reviews.models import UserRole


class IsAuthenticatedOrOwnerReadOnly(permissions.BasePermission):
    """
    Чтение или авторизованный пользователь.

    Разрешает безопасные методы (чтение) всем пользователям,
    а права на запись — только аутентифицированным пользователям
    и владельцу объекта.
    """

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Выполнение запроса на конкретном объекте."""
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешения на запись разрешены только владельцу объекта
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):

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
    """
    Кастомное разрешение прав доступа для администраторов.

    Разрешает доступ только аутентифицированным пользователям
    с ролью администратора или суперпользователя.
    """

    def has_permission(self, request, view):
        """Определяет, имеет ли пользователь право на выполнение запроса."""
        if request.user.is_authenticated:
            is_admin = request.user.role == UserRole.ADMIN.value
            return is_admin or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """Выполнение запроса на конкретном объекте."""
        return self.has_permission(request, view)


class IsAdminModerator(permissions.BasePermission):
    """Кастомное разрешение прав доступа для администраторов и модераторов."""

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
