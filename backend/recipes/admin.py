from django.contrib import admin

from .models import Recipe, RecipeIngredients, Tag, Ingredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientInline(admin.StackedInline):
    model = RecipeIngredients
    fk_name = 'recipe'
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at')
    readonly_fields = ('favorites_count',)
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (IngredientInline,)

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.in_favorites.count()


admin.site.empty_value_display = 'Не задано'
