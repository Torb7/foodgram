from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Exists, Value, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients
from users.models import Follow, Favorites, ShoppingCart
from .filters import RecipeFilter, IngredientSearchFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    SubscriptionSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeMinifiedSerializer,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Управление пользователями."""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.all()

        following = self.request.user.following.filter(pk=OuterRef('pk'))

        return User.objects.annotate(is_subscribed=Exists(following))

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        return super().me(request)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        serializer = AvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @avatar.mapping.delete
    def avatar_delete(self, request):
        request.user.avatar.delete(save=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = (
            request.user.following.all()
            .prefetch_related('recipes')
            .annotate(
                recipes_count=Count('recipes'), is_subscribed=Value(True)
            )
        )
        page = self.paginate_queryset(queryset)

        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        following = get_object_or_404(
            self.get_queryset()
            .prefetch_related('recipes')
            .annotate(recipes_count=Count('recipes')),
            pk=id,
        )

        if following == request.user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        _, created = Follow.objects.get_or_create(
            user=request.user, following=following
        )
        if not created:
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )

        following.is_subscribed = True

        serializer = SubscriptionSerializer(
            following, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id):
        following = get_object_or_404(User.objects.all(), pk=id)

        deleted_count, _ = Follow.objects.filter(
            user=request.user, following=following
        ).delete()
        if not deleted_count:
            raise serializers.ValidationError(
                'Вы не подписаны на этого пользователя.'
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Управление тегами рецептов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Управление ингредиентами рецептов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Управление рецептами."""

    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer

        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags', 'recipe_ingredients__ingredient'
        )

        if not self.request.user.is_authenticated:
            return queryset

        return queryset.user_annotations(self.request.user)

    def add_to(self, model, user, pk, place):
        recipe = get_object_or_404(Recipe, pk=pk)

        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise serializers.ValidationError(f'Рецепт уже есть в {place}.')

        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from(self, model, user, pk, place):
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = model.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if not deleted_count:
            raise serializers.ValidationError(f'Рецепта нет в {place}.')

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.add_to(Favorites, request.user, pk, 'избранном')

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        return self.remove_from(Favorites, request.user, pk, 'избранном')

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__in=request.user.shopping_cart.all()
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        shopping_list = '\n'.join(
            f'{item["ingredient__name"]}: '
            f'{item["amount"]}'
            f'{item["ingredient__measurement_unit"]}.'
            for item in ingredients
        )

        response = HttpResponse(
            shopping_list,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.add_to(ShoppingCart, request.user, pk, 'списке покупок')

    @shopping_cart.mapping.delete
    def shopping_cart_delete_recipe(self, request, pk):
        return self.remove_from(
            ShoppingCart, request.user, pk, 'списке покупок'
        )

    @action(detail=True, url_path='get-link')
    def get_short_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        short_link = request.build_absolute_uri(f'/s/{recipe.short_code}/')

        return Response({'short-link': short_link})
