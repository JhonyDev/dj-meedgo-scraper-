from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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

    latitude = models.FloatField(default=None, null=True, blank=True)
    longitude = models.FloatField(default=None, null=True, blank=True)

    date_of_birth = models.DateField(default=None, null=True, blank=True)

    full_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)

    aadhar_card = models.CharField(max_length=150, null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    type = models.CharField(max_length=25, null=False, blank=False, default='Admin', choices=USER_TYPES)
    phone_number = models.CharField(max_length=50, default=None, null=True, blank=True)
    type_of_ownership = models.CharField(max_length=25, null=True, blank=True, default=None, choices=TYPES_OF_OWNERSHIP)

    pan_number = models.CharField(max_length=100, null=True, blank=True, default=None)
    business_name = models.CharField(max_length=100, null=True, blank=True, default=None)

    is_store_photo_approved = models.BooleanField(default=False)
    is_aadhar_card_approved = models.BooleanField(default=False)
    is_pan_card_approved = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=16, blank=True, null=True, default=None)
    otp_created = models.DateTimeField(null=True, blank=True, default=None)
    otp_sent = models.BooleanField(default=False)

    postal_code = models.CharField(
        max_length=10, null=False, blank=False,
        help_text='Enter a valid postal code (e.g., 12345 or 12345-6789).',
    )

    """BUSINESS ADDRESS DETAILS"""
    address_line_1 = models.CharField(max_length=150, null=True, blank=True, default=None)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True, default=None)
    geo_address = models.CharField(max_length=150, null=True, blank=True, default=None)
    city_town_name = models.CharField(max_length=150, null=True, blank=True, default=None)
    state_name = models.CharField(max_length=150, null=True, blank=True, default=None)
    country = models.CharField(max_length=150, null=True, blank=True, default=None)

    pin_code = models.PositiveIntegerField(null=True, blank=True, default=None)
    shop_name = models.CharField(max_length=150, null=True, blank=True, default=None)
    gst_number = models.PositiveIntegerField(null=True, blank=True, default=None)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if SocialAccount.objects.filter(user=self).exists():
            self.is_active = True
        super().save(*args, **kwargs)

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
        if self.username is None:
            self.username = self.email
            self.save()
        return self.username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class License(models.Model):
    license_name = models.CharField(max_length=150, null=False, blank=False)

    def __str__(self):
        return str(self.license_name)

    class Meta:
        ordering = ['-pk']


class LicenseEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
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


class UserTime(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    opening_time = models.TimeField()
    closing_time = models.TimeField()


class AuthenticationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100, default=None, null=True, blank=True)

    class Meta:
        ordering = ['-pk']


class CustomUserWarning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default=None, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)

    class Meta:
        ordering = ['-pk']


class WarningConfig(models.Model):
    ping = models.TextField(default=None, null=True, blank=True)

    class Meta:
        ordering = ['-pk']


@receiver(post_save, sender=SocialAccount)
def update_user_active_status(sender, instance, created, **kwargs):
    print("Instance Signal received")
    if created:
        print("Changing user state")
        instance.user.is_active = True
        instance.user.save()
