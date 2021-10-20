from django.contrib import admin
from .models import FriendList, Like, Report


class FriendListAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'friend', 'created_on']


class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'liked_by', 'liked_to', 'created_on']


class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'target', 'is_active', 'created_on']


admin.site.register(FriendList, FriendListAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Report, ReportAdmin)
