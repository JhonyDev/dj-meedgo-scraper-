from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_resized import ResizedImageField
import random


"""
At the start please be careful to start migrations
--------------------------------------------------

STEP: 1 comment current_subscription [FIELD] in model [USER]
STEP: 1 py manage.py make migrations accounts
STEP: 2 py manage.py migrate
Then do next ...

"""


class User(AbstractUser):
    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other'),
    )

    profile_image = ResizedImageField(
        upload_to='accounts/images/profiles/', null=True, blank=True, size=[100, 100], quality=75, force_format='PNG',
        help_text='size of logo must be 100*100 and format must be png image file', crop=['middle', 'center']
    )

    bio = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=19, null=True, blank=True)
    profession = models.CharField(max_length=13, null=False, blank=False, default='undefined')
    age = models.PositiveBigIntegerField(default=25, null=False, blank=False)

    interests = models.TextField(null=True, blank=True)
    matching = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, default='m', null=False, blank=False, choices=GENDER_CHOICES)
    interested_lower_age = models.PositiveIntegerField(default=25, null=False, blank=False)
    interested_upper_age = models.PositiveIntegerField(default=50, null=False, blank=False)
    interested_in_gender = models.CharField(max_length=1, default='m', null=False, blank=False, choices=GENDER_CHOICES)

    likes = models.PositiveIntegerField(default=0, null=False, blank=False)
    likers = models.PositiveIntegerField(default=0, null=False, blank=False)
    friends = models.PositiveIntegerField(default=0, null=False, blank=False)

    expiry_date = models.DateField(default=None, null=True, blank=True)
    is_paid = models.BooleanField(default=False, null=False, blank=False)
    is_identified = models.BooleanField(default=False, null=False, blank=False)

    address = models.CharField(max_length=255, default='not-provided', null=False, blank=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'User Account'
        verbose_name_plural = 'Users Accounts'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.matching = random.randint(50, 100)
        super(User, self).save(*args, **kwargs)



class UserImage(models.Model):
    image = models.ImageField(upload_to='accounts/images/profiles/', null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, related_name='images',
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
