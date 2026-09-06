from django.db.models import Count, OuterRef, Exists, Value, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients
from users.models import User
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    SetPasswordSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeMinifiedSerializer,
)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Управление пользователями."""

    def get_permissions(self):
        if self.action in ('list', 'create', 'retrieve'):
            return [AllowAny()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer

        return UserSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.all()

        following = self.request.user.following.filter(pk=OuterRef('pk'))

        return User.objects.annotate(is_subscribed=Exists(following))

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user)

        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)

        else:
            request.user.avatar.delete(save=True)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
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

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        following = get_object_or_404(
            self.get_queryset()
            .prefetch_related('recipes')
            .annotate(recipes_count=Count('recipes')),
            pk=pk,
        )

        if request.method == 'POST':

            if following == request.user:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя.'
                )

            if following.is_subscribed:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя.'
                )

            request.user.following.add(following)
            following.is_subscribed = True

            serializer = SubscriptionSerializer(
                following, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if not following.is_subscribed:
                raise serializers.ValidationError(
                    'Вы не подписаны на этого пользователя.'
                )

            request.user.following.remove(following)

            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Управление тегами рецептов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Управление ингредиентами рецептов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (SearchFilter,)
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

        favorite_recipes = self.request.user.favorite_recipes.filter(
            pk=OuterRef('pk')
        )
        shopping_cart = self.request.user.shopping_cart.filter(
            pk=OuterRef('pk')
        )
        following = self.request.user.following.filter(pk=OuterRef('author'))

        return queryset.annotate(
            is_favorited=Exists(favorite_recipes),
            is_in_shopping_cart=Exists(shopping_cart),
            is_subscribed=Exists(following),
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False

        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':

            if recipe.in_favorites.filter(pk=request.user.pk).exists():
                raise serializers.ValidationError(
                    'Рецепт уже есть в избранном.'
                )

            request.user.favorite_recipes.add(recipe)

            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if not recipe.in_favorites.filter(pk=request.user.pk).exists():
                raise serializers.ValidationError('Рецепта нет в избранном.')

            request.user.favorite_recipes.remove(recipe)

            return Response(status=status.HTTP_204_NO_CONTENT)

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
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':

            if recipe.in_shopping_cart.filter(pk=request.user.pk).exists():
                raise serializers.ValidationError(
                    'Рецепт уже есть в списке покупок.'
                )

            recipe.in_shopping_cart.add(request.user)

            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if not recipe.in_shopping_cart.filter(pk=request.user.pk).exists():
                raise serializers.ValidationError(
                    'Рецепт нет в списке покупок.'
                )

            recipe.in_shopping_cart.remove(request.user)

            return Response(status=status.HTTP_204_NO_CONTENT)
