from django.contrib import admin
from .models import FriendList, Like, Report, MpesaTransaction


class FriendListAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'friend', 'created_on']
    search_fields = ['id', 'user__username', 'friend__username']


class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'liked_by', 'liked_to', 'like_type', 'created_on']
    list_filter = ['like_type']
    search_fields = ['id', 'liked_by__username', 'liked_to__username']


class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'target', 'is_active', 'created_on']
    list_filter = ['is_active']
    search_fields = ['id', 'user__username', 'target__username']


admin.site.register(FriendList, FriendListAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(MpesaTransaction)
admin.site.register(Report, ReportAdmin)
