from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q

User = get_user_model()


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, email=None, phone_number=None, password=None):
        if username:
            user = User.objects.filter(
                Q(username=username)
            ).first()
        elif email:
            user = User.objects.filter(
                Q(email=email)
            ).first()
        elif phone_number:
            user = User.objects.filter(
                Q(phone_number=phone_number)
            ).first()
        else:
            return None

        if not user:
            return None
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
