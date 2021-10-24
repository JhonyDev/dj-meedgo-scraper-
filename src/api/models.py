from django.conf import settings
from django.db import models


class FriendList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="has_friends")
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Friend List"
        verbose_name_plural = "Friend Lists"

    def __str__(self):
        return str(self.pk)


class Like(models.Model):
    LIKE_TYPE = (
        ('l', 'LIKE'),
        ('f', 'FAVOURITE')
    )

    liked_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="liked_by", blank=True)
    liked_to = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="liked_to")
    like_type = models.CharField(max_length=1, choices=LIKE_TYPE, default=1)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super(Like, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Like, self).delete(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'


class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    target = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='target')

    is_active = models.BooleanField(default=True, null=False, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)
