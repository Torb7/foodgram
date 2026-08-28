import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import User
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')

        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])

        return user


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
        else:
            raise serializers.ValidationError('Ожидается строка Base64.')

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
