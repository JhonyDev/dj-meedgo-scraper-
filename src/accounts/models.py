from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django_resized import ResizedImageField


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
    phone_number = models.CharField(max_length=50, default=None, null=True, blank=True)
    # postal_code = models.PositiveIntegerField(max_length=50, default=None, null=True, blank=True)
    postal_code = models.CharField(
        max_length=10, null=False, blank=False,
        help_text='Enter a valid postal code (e.g., 12345 or 12345-6789).',
        validators=[
            RegexValidator(
                regex=r'^\d{5}(-\d{4})?$',
                message='Enter a valid postal code (e.g., 12345 or 12345-6789).'
            )
        ]
    )

    # user_password = models.CharField(max_length=50, default=None, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'User Account'
        verbose_name_plural = 'Users Accounts'

    def __str__(self):
        return self.username
