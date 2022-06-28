import datetime

import jwt
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .models import User


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            print(token)
            id = decode_access_token(token)
            user = User.objects.get(pk=id)
            return user, None
        raise exceptions.AuthenticationFailed('Unauthenticated')


def create_access_token(user, is_new_registration):
    return jwt.encode({
        'is_new_registration': is_new_registration,
        'user': user,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5),
        'iat': datetime.datetime.utcnow()
    }, 'access_secret', algorithm='HS256')


def decode_access_token(token):
    try:
        payload = jwt.decode(token, 'access_secret', algorithms='HS256')
        return payload['user']['pk']
    except:
        raise exceptions.AuthenticationFailed('Unuthenticated')


def create_refresh_token(id):
    return jwt.encode({
        'user_id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }, 'refresh_secret', algorithm='HS256')


def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, 'refresh_secret', algorithms='HS256')

        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('Unuthenticated')
