from django.conf import settings
from django.db import models


class FriendList(models.Model):
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="has_friends")
   friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="is_friend")
   created_on = models.DateTimeField(auto_now_add=True)

   class Meta :
       ordering = ['-id']
       verbose_name = "Firend List"
       verbose_name_plural = "Friend Lists"

   def __str__(self):
       return f"User {self.user} has a friend {self.friend}"


class Like(models.Model):
    liked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_by")
    liked_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_to")
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ''

    class Meta:
        ordering = ['-id']
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'   