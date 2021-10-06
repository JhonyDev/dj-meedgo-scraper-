from django.db.models import fields
from django.db.models.base import Model
from src.api.models import FriendList, Like
from rest_framework import serializers

from src.accounts.models import User, UserImage


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = "__all__"
        read_only_fields = [
            'pk', 'user', 'created_on'
        ]


class UserFriendListSerializer(serializers.Serializer):
    class Meta:
        model = FriendList
        fields = [
            'friend', 'created_on'
        ]


class UserPasswordChangeSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    images = UserImageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email', 'phone_number',
            'likes', 'friends', 'address', 'date_joined', 'last_login', 'images'
        ]
        read_only_fields = [
            'email', 'date_joined', 'last_login', 'username', 'likes', 'friends', 'images'
        ]


class UserLikersSerializer(serializers.Serializer):
    liked_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Like
        fields = [
            'liked_by', 'created_on'
        ]


class UserLikesSerializer(serializers.Serializer):
    liked_to = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Like
        fields = [
            'liked_to', 'created_on'
        ]


class UserNewsFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email', 'phone_number',
            'likes', 'friends', 'address'
        ]
        read_only_fields = [
            'first_name', 'last_name', 'username', 'email', 'phone_number',
            'likes', 'friends', 'address'
        ]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = [
            'pk', 'liked_by', 'created_on'
        ]
