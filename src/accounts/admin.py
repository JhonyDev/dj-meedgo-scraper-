from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User, UserImage
)


class UserAdminCustom(admin.ModelAdmin):
    list_display = [
        'pk', 'username', 'first_name', 'last_name',
        'email', 'gender', 'is_paid', 'is_identified', 'is_active', 'date_joined'
    ]
    list_filter = ['gender', 'is_paid', 'is_identified', 'is_superuser', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']


class UserImageAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'image', 'user', 'created_on'
    ]
    search_fields = ['pk', 'user__username']


admin.site.register(User, UserAdminCustom)
admin.site.register(UserImage, UserImageAdmin)
# admin.site.register(User, UserAdmin)


admin.site.site_header = "SIMBO - Admin"
admin.site.site_title = "SIMBO - Admin"
admin.site.index_title = "SIMBO - Administration"