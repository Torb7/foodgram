from django.contrib import admin
from django.db.models import Count

from .models import Recipe, RecipeIngredients, Tag, Ingredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')
    readonly_fields = ('recipes_count',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(recipes_count=Count('recipes'))
        )

    @admin.display(description='Количество рецептов с этим тегом')
    def recipes_count(self, obj):
        return obj.recipes_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name',)
    readonly_fields = ('recipes_count',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(recipes_count=Count('recipes'))
        )

    @admin.display(description='Количество рецептов с этим ингридиентом')
    def recipes_count(self, obj):
        return obj.recipes_count


class IngredientInline(admin.StackedInline):
    model = RecipeIngredients
    fk_name = 'recipe'
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at')
    readonly_fields = ('favorites_count',)
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (IngredientInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(favorites_count=Count('in_favorites'))
        )

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites_count


admin.site.empty_value_display = 'Не задано'
