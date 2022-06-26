from rest_framework import serializers

from . import models


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserDetail
        fields = '__all__'
        read_only_fields = [
            'user'
        ]
