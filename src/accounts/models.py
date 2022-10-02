from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField

"""
At the start please be careful to start migrations
--------------------------------------------------

STEP: 1 comment current_subscription [FIELD] in model [USER]
STEP: 1 py manage.py make migrations accounts
STEP: 2 py manage.py migrate
Then do next ...

"""


class User(AbstractUser):
    USER_TYPES = (
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
    )

    profile_image = ResizedImageField(
        upload_to='accounts/images/profiles/', null=True, blank=True, quality=60, force_format='PNG',
        help_text='size of logo must be 100*100 and format must be png image file', crop=['middle', 'center']
    )
    type = models.CharField(max_length=25, null=False, blank=False, default='Admin', choices=USER_TYPES)
    user_password = models.CharField(max_length=50, default=None, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'User Account'
        verbose_name_plural = 'Users Accounts'

    def __str__(self):
        return self.username
