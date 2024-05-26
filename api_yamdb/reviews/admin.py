from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User

admin.site.site_header = 'Панель администратора'
admin.site.site_title = 'Панель администратора'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year')
    list_filter = ('year', 'genre', 'category')
    search_fields = ('name', 'description')
    empty_value_display = 'Ничего нет'


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'bio',
        'role',
        'email')
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = 'Ничего нет'
    list_editable = ('role',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title_id',
        'author',
        'score',
        'pub_date'
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'review_id',
        'text',
        'pub_date'
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
