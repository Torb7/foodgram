from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    tags = filters.CharFilter(method='filter_tags')
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')

        for tag in tags:
            queryset = queryset.filter(tags__slug=tag)

        return queryset.distinct()

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset

        if value == 1:
            return queryset.filter(in_favorites=self.request.user)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset

        if value == 1:
            return queryset.filter(in_shopping_cart=self.request.user)

        return queryset


class IngredientSearchFilter(SearchFilter):
    """Фильтр для рецептов."""

    search_param = 'name'
