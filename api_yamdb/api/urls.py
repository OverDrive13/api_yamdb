from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    UserViewSet, get_token, signup
)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='review')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment')
router_v1.register('users', UserViewSet, basename='users')


auth_endpoints_v1 = [
    path('signup/', signup, name='get_code'),
    path('token/', get_token, name='get_token')
]

urlpatterns = [
    path('v1/auth/', include(auth_endpoints_v1)),
    path('v1/', include(router_v1.urls)),
]
