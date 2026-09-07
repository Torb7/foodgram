from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Follow


class FollowsInline(admin.TabularInline):
    model = Follow
    fk_name = 'user'
    extra = 0


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    filter_horizontal = ('favorite_recipes', 'shopping_cart')
    inlines = (FollowsInline,)


BaseUserAdmin.fieldsets += (  # type: ignore[operator]
    (
        'Связанные объекты',
        {'fields': ('favorite_recipes', 'shopping_cart')},
    ),
)

admin.site.empty_value_display = 'Не задано'
