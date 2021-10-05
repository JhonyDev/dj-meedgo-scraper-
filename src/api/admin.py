from django.contrib import admin
from .models import FriendList, Like


class FriendListAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'friend', 'created_on']


class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'liked_by', 'liked_to', 'created_on']


admin.site.register(FriendList, FriendListAdmin)
admin.site.register(Like, LikeAdmin)
