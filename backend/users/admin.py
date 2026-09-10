from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, Favorites, ShoppingCart

User = get_user_model()


class FollowsInline(admin.TabularInline):
    model = Follow
    fk_name = 'user'
    extra = 0


class FavoritesInline(admin.TabularInline):
    model = Favorites
    fk_name = 'user'
    extra = 0


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    fk_name = 'user'
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    inlines = (FollowsInline, FavoritesInline, ShoppingCartInline)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user', 'following')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


admin.site.empty_value_display = 'Не задано'
