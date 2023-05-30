from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
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

    def clean(self):
        if self.username is None and self.email is None and self.phone_number:
            raise ValidationError("Either username or email must be provided.")
        if self.email and User.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("Email already registered.")
        if self.username and User.objects.filter(email=self.username).exclude(pk=self.pk).exists():
            raise ValidationError("Username already registered.")
        if self.phone_number and User.objects.filter(email=self.phone_number).exclude(pk=self.pk).exists():
            raise ValidationError("Phone Number already registered.")

    class Meta:
        ordering = ['-id']
        verbose_name = 'User Account'
        verbose_name_plural = 'Users Accounts'

    def __str__(self):
        return self.username
