from django.db.models import Count, OuterRef, Exists, Value
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    SetPasswordSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
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
