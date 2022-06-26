from rest_framework import permissions, generics

from . import serializers


class PostRegistrationFormView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserDetailsSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
