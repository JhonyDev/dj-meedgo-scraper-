from django.contrib import admin
from django.utils.html import format_html

from .models import FriendList, Like, Report, MpesaTransaction


class FriendListAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_view', 'friend_view', 'friends', 'likes', 'likers', 'created_on']
    search_fields = ['id', 'user__username', 'friend__username']

    def user_view(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.user.pk, obj.user.username
        )

    def friend_view(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.friend.pk, obj.friend.username
        )

    def friends(self, obj):
        return FriendList.objects.filter(user=obj.user.pk).count()

    def likes(self, obj):
        ls = Like.objects.filter(liked_by=obj.user.pk, like_type='l').count()
        fs = Like.objects.filter(liked_by=obj.user.pk, like_type='f').count()

        return f"{ls} likes  -  {fs} favs"

    def likers(self, obj):
        ls = Like.objects.filter(liked_to=obj.user.pk, like_type='l').count()
        fs = Like.objects.filter(liked_to=obj.user.pk, like_type='f').count()

        return f"{ls} likes  -  {fs} favs"


class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'liker', 'liked', 'like_type', 'created_on']
    list_filter = ['like_type']
    search_fields = ['id', 'liked_by__username', 'liked_to__username']

    def liker(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.liked_by.pk, obj.liked_by.username
        )

    def liked(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.liked_to.pk, obj.liked_to.username
        )


class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_view', 'target_view', 'is_active', 'created_on']
    list_filter = ['is_active']
    search_fields = ['id', 'user__username', 'target__username']

    def user_view(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.user.pk, obj.user.username
        )

    def target_view(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.target.pk, obj.target.username
        )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_view', 'purpose', 'request_id', 'amount', 'completed', 'created_on', 'expires_on']
    list_filter = ['completed']
    search_fields = ['id', 'user_id__username', 'user_id__email', 'request_id']

    def user_view(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.user_id.pk, obj.user_id.username
        )


admin.site.register(FriendList, FriendListAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(MpesaTransaction, TransactionAdmin)
admin.site.register(Report, ReportAdmin)
