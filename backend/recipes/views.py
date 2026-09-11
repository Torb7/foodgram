from django.shortcuts import redirect

from .models import Recipe


def short_link_redirect(request, short_code):
    """Перенаправление c короткой ссылки на эндпоинт рецепта."""

    try:
        recipe = Recipe.objects.get(short_code=short_code)

    except Recipe.DoesNotExist:
        return redirect('/404/')

    return redirect(f'/recipes/{recipe.id}/')
