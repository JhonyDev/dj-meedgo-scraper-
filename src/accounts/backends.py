from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, email=None, phone_number=None, password=None):
        if username:
            user = User.objects.filter(
                username=username
            ).first()
            if user.check_password(password):
                return user

        if email:
            user = User.objects.filter(
                email=email
            ).first()

            if user.check_password(password):
                return user

        if phone_number:
            user = User.objects.filter(
                phone_number=phone_number
            ).first()
            if user.check_password(password):
                return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
