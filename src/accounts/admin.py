from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User, UserImage
)


class UserAdminCustom(admin.ModelAdmin):
    list_display = [
        'pk', 'username', 'first_name', 'last_name',
        'email', 'gender', 'is_paid', 'is_identified'
    ]
    list_filter = ['gender', 'is_paid', 'is_identified', 'is_superuser', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']


admin.site.register(User, UserAdminCustom)
admin.site.register(UserImage)
# admin.site.register(User, UserAdmin)
