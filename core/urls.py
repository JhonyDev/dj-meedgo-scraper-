"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from .settings import DEBUG, MEDIA_ROOT, MEDIA_URL

schema_view = get_schema_view(
    openapi.Info(
        title='Meedgo API',
        default_version='v1',
        description='Meedgo API Built using DRF',
        # terms_of_service='https://www.example.com/terms/',
        contact=openapi.Contact(email='junaid@jhonydev.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
)

swagger_patterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
# urls.py

urlpatterns = [
    # ADMIN/ROOT APPLICATION
    path('admin/', admin.site.urls),
    path('auth/', include('src.accounts.urls', namespace='api')),

    # WEBSITE APPLICATION --------------------------------------------------------------------------------
    # path('accounts/', include('src.accounts.urls', namespace='accounts')),

    # REST API -------------------------------------------------------------------------------------------
    # path('auth/login/', CustomLoginView.as_view(), name='login-user'),
    # path('auth/registration/', CustomRegisterAccountView.as_view(), name='account_create_new_user'),
    # path('auth/', include('dj_rest_auth.urls')),

    path('api/', include('src.api.urls', namespace='api')),
    # path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('allauth.urls')),
] + swagger_patterns

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
