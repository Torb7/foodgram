from django.db.models import OuterRef, Exists, Value
from django.db import models


class RecipeQuerySet(models.QuerySet):
    def user_annotations(self, user):
        if not user.is_authenticated:
            return self.annotate(
                is_favorited=Value(False),
                is_in_shopping_cart=Value(False),
                is_subscribed=Value(False),
            )

        favorite_recipes = user.favorite_recipes.filter(pk=OuterRef('pk'))
        shopping_cart = user.shopping_cart.filter(pk=OuterRef('pk'))
        following = user.following.filter(pk=OuterRef('author'))

        return self.annotate(
            is_favorited=Exists(favorite_recipes),
            is_in_shopping_cart=Exists(shopping_cart),
            is_subscribed=Exists(following),
        )
