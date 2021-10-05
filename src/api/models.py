from django.conf import settings
from django.db import models

from src.api.bll import create_like_logic, delete_like_logic


class FriendList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="has_friends")
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="is_friend")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Firend List"
        verbose_name_plural = "Friend Lists"

    def __str__(self):
        return str(self.pk)


class Like(models.Model):
    LIKE_TYPE = (
        (1, 'LIKE'),
        (2, 'FAVOURITE')
    )
    liked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_by", blank=True)
    liked_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_to")
    like_type = models.CharField(max_length=1, choices=LIKE_TYPE, default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        create_like_logic(self)
        super(Like, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_like_logic(self)
        super(Like, self).delete(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
