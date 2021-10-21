from django.db.models import fields
from django.db.models.base import Model
from src.api.models import FriendList, Like, Report
from rest_framework import serializers

from src.accounts.models import User, UserImage


# NESTED SERIALIZERS REQUIRED MODEL CHECKUP [related_name]
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = "__all__"
        read_only_fields = [
            'pk', 'user', 'created_on'
        ]


class UserPasswordChangeSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'profile_image', 'first_name', 'last_name', 'username', 'age',
            'gender', 'profession', 'matching'
        ]


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'pk', 'profile_image', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'age', 'bio', 'about', 'address',
            'interests', 'matching', 'gender', 'interested_lower_age', 'interested_upper_age', 'interested_in_gender',
            'likes', 'likers', 'friends', 'date_joined', 'address', 'expiry_date', 'is_paid', 'is_identified'
        ]
        read_only_fields = [
            'email', 'likes', 'likers', 'friends', 'date_joined', 'expiry_date', 'is_paid', 'is_identified',
            'images', 'matching'
        ]


class UserLikersSerializer(serializers.Serializer):
    liked_by = UserPublicSerializer(many=False, read_only=True)

    class Meta:
        model = Like
        fields = [
            'liked_by', 'created_on'
        ]


class UserLikesSerializer(serializers.Serializer):
    liked_to = UserPublicSerializer(many=False, read_only=True)

    class Meta:
        model = Like
        fields = [
            'liked_to', 'created_on'
        ]


class FriendSerializer(serializers.ModelSerializer):
    friend = UserPublicSerializer(many=False, read_only=True)

    class Meta:
        model = FriendList
        fields = ['pk', 'friend', 'created_on']


class LikeSerializer(serializers.ModelSerializer):
    liked_to = UserPublicSerializer(many=False, read_only=True)

    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = [
            'pk', 'liked_by', 'created_on'
        ]


class LikeAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = [
            'pk', 'liked_by', 'created_on'
        ]


class ReportSerializer(serializers.ModelSerializer):
    target = UserPublicSerializer(many=False, read_only=True)

    class Meta:
        model = Report
        fields = [
            'pk', 'target', 'is_active', 'created_on'
        ]
        read_only_fields = [
            'pk', 'is_active', 'created_on'
        ]

# def save(self):
#     like = Like(
#         liked_to=self.validated_data['liked_to']
#     )
#     print(like.liked_by)
#     print(like.liked_to)
#
#     # if password != password2:
#     #     raise serializers.ValidationError({'password': 'Passwords must be matched'})
#     # if EmailAddress.objects.filter(email=email):
#     #     raise serializers.ValidationError({'email': 'Email is already registered'})
#     like.save()
#     return like
