from django.db.models import OuterRef, Exists
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from users.models import User
from .serializers import UserSerializer, UserCreateSerializer


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
