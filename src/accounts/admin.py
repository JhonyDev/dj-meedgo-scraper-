from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User, UserImage
)


admin.site.register(User)
admin.site.register(UserImage)
# admin.site.register(User, UserAdmin)
