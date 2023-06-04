from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django_resized import ResizedImageField

from core.settings import SOLE_PROPRIETORSHIP, PARTNERSHIP, LIMITED_LIABILITY_PARTNERSHIP, ONE_PERSON_COMPANY, \
    PRIVATE_LIMITED, PUBLIC_LIMITED, HINDU_UNDIVIDED_FAMILY


class User(AbstractUser):
    USER_TYPES = (
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
    )

    TYPES_OF_OWNERSHIP = (
        (SOLE_PROPRIETORSHIP, 'Sole Proprietorship'),
        (PARTNERSHIP, 'Partnership'),
        (LIMITED_LIABILITY_PARTNERSHIP, 'Limited liability Partnership'),
        (ONE_PERSON_COMPANY, 'One Person Company'),
        (PRIVATE_LIMITED, 'Private Limited'),
        (PUBLIC_LIMITED, 'Public Limited'),
        (HINDU_UNDIVIDED_FAMILY, 'Hindu Undivided Family Business'),
    )

    profile_image = ResizedImageField(
        upload_to='accounts/images/profiles/', null=True, blank=True, quality=60, force_format='PNG',
        help_text='size of logo must be 100*100 and format must be png image file', crop=['middle', 'center']
    )

    pan_card_image = ResizedImageField(
        upload_to='accounts/images/pan_cards/', null=True, blank=True, quality=60, force_format='PNG',
        help_text='Format must be png image file', crop=['middle', 'center']
    )
    store_photo = ResizedImageField(
        upload_to='accounts/images/pan_cards/', null=True, blank=True, quality=60, force_format='PNG',
        help_text='Format must be png image file', crop=['middle', 'center']
    )
    is_store_photo_approved = models.BooleanField(default=False)

    full_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)

    aadhar_card = models.CharField(max_length=150, null=True, blank=True)
    is_aadhar_card_approved = models.BooleanField(default=False)

    email = models.EmailField(null=True, blank=True)
    type = models.CharField(max_length=25, null=False, blank=False, default='Admin', choices=USER_TYPES)
    phone_number = models.CharField(max_length=50, default=None, null=True, blank=True)
    type_of_ownership = models.CharField(max_length=25, null=True, blank=True, default=None, choices=TYPES_OF_OWNERSHIP)

    pan_number = models.CharField(max_length=100, null=True, blank=True, default=None)
    business_name = models.CharField(max_length=100, null=True, blank=True, default=None)
    is_pan_card_approved = models.BooleanField(default=False)

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

    """BUSINESS ADDRESS DETAILS"""
    address_line_1 = models.CharField(max_length=150, null=True, blank=True, default=None)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True, default=None)
    city_town_name = models.CharField(max_length=150, null=True, blank=True, default=None)
    state_name = models.CharField(max_length=150, null=True, blank=True, default=None)
    country = models.CharField(max_length=150, null=True, blank=True, default=None)
    pin_code = models.PositiveIntegerField(null=True, blank=True, default=None)
    shop_name = models.CharField(max_length=150, null=True, blank=True, default=None)
    gst_number = models.PositiveIntegerField(null=True, blank=True, default=None)

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


class License(models.Model):
    license_name = models.CharField(max_length=150, null=False, blank=False)

    def __str__(self):
        return str(self.license_name)

    class Meta:
        ordering = ['-pk']


class LicenseEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)
    license_number = models.PositiveIntegerField(default=None, null=True, blank=True)
    license_expiry = models.DateField(default=None, null=True, blank=True)
    license_image = ResizedImageField(
        upload_to='accounts/images/licenses/', null=True, blank=True, quality=60, force_format='PNG',
        help_text='Format must be png image file', crop=['middle', 'center']
    )

    def __str__(self):
        return f'{str(self.user)} - {self.license} - {self.license_number}'

    class Meta:
        ordering = ['-pk']
