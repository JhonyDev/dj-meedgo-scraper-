"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import logging
import os
from datetime import timedelta
from pathlib import Path

import environ

""" VAR ----------------------------------------------------------------------------------------"""
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
ROOT_URLCONF = 'core.urls'
AUTH_USER_MODEL = 'accounts.User'

env_file = os.path.join(BASE_DIR, ".env")
env = environ.Env()
env.read_env(env_file)

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = env('SERVER_KEY')
# SECURITY WARNING: keep the secret key used in production secret!
SERVER = env('SERVER') == 'True'
DEBUG = env('DEBUG') == 'True'

SOLE_PROPRIETORSHIP = 'SP'
PARTNERSHIP = 'P'
LIMITED_LIABILITY_PARTNERSHIP = 'LLP'
ONE_PERSON_COMPANY = 'OPC'
PRIVATE_LIMITED = 'PL'
PUBLIC_LIMITED = 'PPL'
HINDU_UNDIVIDED_FAMILY = 'HUF'
NET_MEDS = 'Netmeds'
ONE_MG = '1Mg'
PHARM_EASY = 'PharmEasy'
FLIPCART = 'Flipkart Health'
FIRST_MESSAGE_WHEN_ORDER_ACCEPTED = 'Hi, I have accepted your offer.'

LIST_PLATFORMS = [NET_MEDS, ONE_MG, PHARM_EASY, FLIPCART]
LOGIN_REDIRECT_URL = '/auth/google-callback/'

PLATFORMS = (
    ('1', NET_MEDS),
    ('2', ONE_MG),
    ('3', PHARM_EASY),
    ('4', FLIPCART),
)

GOOGLE_CLIENT_ID = "267690366244-ql55e38j75vj1mlkqctja4oh8l4jek27.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

# PAYTM_MERCHANT_ID = 'QlrInG17260337389232'
# PAYTM_SECRET_KEY = 'kbzk1DSbJiV_03p5'
# PAYTM_WEBSITE = 'WEBSTAGING'  # Replace with 'DEFAULT' for production

PAYTM_MERCHANT_ID = 'QlrInG17260337389232'
PAYTM_MERCHANT_KEY = 'jnJg0c7Rbvv13w@t'

PAYTM_WEBSITE = 'WEB'  # Replace with 'DEFAULT' for production
if SERVER:
    SITE_ID = 4
    GOOGLE_CALLBACK_ADDRESS = "https://app.meedgo.com/auth/google-callback/"
    PAYTM_CALLBACK_URL = 'https://app.meedgo.com/api/callback/'
    BASE_URL = "https://app.meedgo.com/"
else:
    SITE_ID = 1
    # GOOGLE_CALLBACK_ADDRESS = "http://127.0.0.1:8000/auth/google-callback/"
    GOOGLE_CALLBACK_ADDRESS = "http://127.0.0.1:8000/accounts/google/login/callback/"
    PAYTM_CALLBACK_URL = 'http://127.0.0.1:8000/api/callback/'
    BASE_URL = "http://127.0.0.1:8000/"

ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3030', 'http://localhost:5173', 'https://meedgo.com', 'http://meedgo.com',
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

""" APPS ---------------------------------------------------------------------------------------"""
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'channels',
    'django.contrib.postgres',

    # OTP LOGIN
    'django_otp',
    'django_otp.plugins.otp_totp',

    # REQUIRED_APPLICATIONS
    'crispy_forms',
    'ckeditor',
    'django_filters',
    'celery',
    'django_celery_results',
    'celery_progress',

    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',

    'rest_framework',
    'rest_framework.authtoken',

    'dj_rest_auth',
    'dj_rest_auth.registration',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    # 'src.accounts',
    'src.accounts.apps.AccountsAppConfig',
    'src.api',
    'src.website',
    'src.notification',
    'drf_yasg',
    'corsheaders',
]
SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'core.urls.swagger_info',
}
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200',  # Replace with your Elasticsearch server details
    },
}

""" MIDDLE WARES ----------------------------------------------------------------------------"""
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
SCRAPY_SETTINGS_MODULE = 'healthplus_medicine_parent.healthplus_medicine.settings'
""" TEMPLATES -------------------------------------------------------------------------------"""
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'src.accounts.authentication.JWTAuthentication',

    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',

}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'src.accounts.serializers.RegisterSerializerRestAPI',
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'src.accounts.backends.CustomAuthBackend',
]

# WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Replace 'myapp' with your Django app namea


""" DATABASES ------------------------------------------------------------------------------------"""
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://127.0.0.1:6379"],
        },
    },
}

if not SERVER:
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.sqlite3',
    #         'NAME': BASE_DIR / 'db.sqlite3',
    #     }
    # }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'admin22',
            'PASSWORD': 'Twitter*222023',
            'HOST': 'meedgodb.postgres.database.azure.com',
            'PORT': '5432',
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'myproject',
            'USER': 'myprojectuser',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

""" VALIDATORS ------------------------------------------------------------------------------------"""

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

""" INTERNATIONALIZATION --------------------------------------------------------------------------"""

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

""" STATIC AND MEDIA -----------------------------------------------------------------------------"""

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

""" OTHER APPS SYSTEM ----------------------------------------------------------------------------"""
CRISPY_TEMPLATE_PACK = 'bootstrap4'

""" LOGIN SYSTEM ---------------------------------------------------------------------------------"""

LOGOUT_REDIRECT_URL = '/admin/'

""" EMAIL SYSTEM ---------------------------------------------------------------------------------"""

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development only
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'care@meedgo.com'
EMAIL_HOST_PASSWORD = 'ibxdeltbsaokriks'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'Meedgo <care@meedgo.com>'

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {
    'JPEG': ".jpg",
    'PNG': ".png",
    'GIF': ".gif"
}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

""" ALL-AUTH SETUP --------------------------------------------------------------------------------"""

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'redirect_uri': GOOGLE_CALLBACK_ADDRESS
        }
    },
    'apple': {
        'APP': {
            'client_id': 'YOUR_APPLE_CLIENT_ID',
            'team_id': 'YOUR_APPLE_TEAM_ID',
            'key_id': 'YOUR_APPLE_KEY_ID',
            'private_key_path': 'path/to/your/private_key.p8',
            'algorithm': 'ES256',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v11.0',
    }
}

CONSUMER_KEY = "S2CgBmt7RBOrskJIsuWpyABnLoPIKBBW"
CONSUMER_SECRET = "QBL45acULAxxtvQl"
PASSKEY = "3c388f8116b610a69eba8110e3ef118078c639af5c1c711ad17a2a74c02c6ed2"
SHORT_CODE = "4075259"
CALLBACK_URL = "https://mateappkenya.com/api/mpesa-stk-confirmation/"

ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
accept_content = ['application/json']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'Asia/Karachi'

# logger = logging.getLogger('elasticsearch')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)
