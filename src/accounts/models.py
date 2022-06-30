from django.conf import settings
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
        ('Patient', 'Patient'),
        ('Admin', 'Admin'),
    )

    profile_image = ResizedImageField(
        upload_to='accounts/images/profiles/', null=True, blank=True, quality=60, force_format='PNG',
        help_text='size of logo must be 100*100 and format must be png image file', crop=['middle', 'center']
    )
    creator = models.ForeignKey('User', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=19, null=True, blank=True)
    age = models.PositiveBigIntegerField(default=25, null=False, blank=False)
    type = models.CharField(max_length=25, null=False, blank=False, default='Patient', choices=USER_TYPES)

    address = models.CharField(max_length=255, default='not-provided', null=False, blank=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'User Account'
        verbose_name_plural = 'Users Accounts'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.email is not None:
            if self.email:
                if User.objects.filter(email=self.email).exists():
                    self.email = ""
        super(User, self).save(*args, **kwargs)


class UserImage(models.Model):
    image = models.ImageField(upload_to='accounts/images/profiles/', null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='images',
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
