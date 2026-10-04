from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar_key']


class RegisterSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists.')
        return value

    def validate_nickname(self, value):
        if Profile.objects.filter(nickname=value).exists():
            raise serializers.ValidationError('User with this nickname already exists.')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({'password_confirm': ['Passwords do not match.']})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        nickname = validated_data.pop('nickname')

        user = User.objects.create_user(password=password, **validated_data)
        user.profile.nickname = nickname
        user.profile.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar_key']

    def validate(self, attrs):
        data = dict(self.initial_data)
        allowed_fields = {'nickname', 'avatar_key'}
        extra_fields = set(data) - allowed_fields

        if extra_fields:
            raise serializers.ValidationError({
                field: ['This field is not allowed.'] for field in sorted(extra_fields)
            })

        return attrs

    def validate_nickname(self, value):
        if self.instance and self.instance.nickname == value:
            return value

        if Profile.objects.filter(nickname=value).exclude(pk=self.instance.pk).exists():
            raise DjangoValidationError('User with this nickname already exists.')

        return value

    def validate_avatar_key(self, value):
        allowed = {choice[0] for choice in Profile.AVATAR_CHOICES}
        if value not in allowed:
            raise DjangoValidationError('Invalid avatar selection.')
        return value
