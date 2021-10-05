from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_resized import ResizedImageField


"""
At the start please be careful to start migrations
--------------------------------------------------

STEP: 1 comment current_subscription [FIELD] in model [USER]
STEP: 1 py manage.py makemigrations accounts
STEP: 2 py manage.py migrate
Then do next ...

"""


class User(AbstractUser):
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    likes = models.PositiveIntegerField(default=0, null=True, blank=True)
    friends = models.PositiveIntegerField(default=0, null=False, blank=False)
    address = models.CharField(max_length=255, default='not-provided', null=False, blank=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'User Account'
        verbose_name_plural = 'Users Accounts'

    def __str__(self):
        return self.username


class UserImage(models.Model):
    image = models.ImageField(upload_to='accounts/images/profiles/', null=False, blank=False)
    is_profile_image = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, related_name='user_image',
                             on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "User Image"
        verbose_name_plural = "User Images"

    def __str__(self):
        return self.image.url

    def delete(self, *args, **kwargs):
        self.image.delete(save=True)
        super(UserImage, self).delete(*args, **kwargs)
