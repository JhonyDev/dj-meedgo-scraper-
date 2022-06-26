from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserDetail(models.Model):
    MARITAL_STATUS = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Divorced', 'Divorced'),
    )
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    office_referral = models.TextField(default='')
    what_brings = models.TextField(default='')
    date_of_birth = models.DateField()
    marital_status = models.CharField(max_length=15, choices=MARITAL_STATUS)
    sex = models.CharField(max_length=15, choices=MARITAL_STATUS)
    name = models.CharField(max_length=15)
    ssn = models.CharField(max_length=25)
    address = models.TextField()
    zip_code = models.IntegerField(default=0)
    cell = models.CharField(max_length=19)
    home_alternate = models.TextField()
    email_address = models.EmailField()
    preferred_pharmacy = models.CharField(max_length=100)
    cross_streets = models.CharField(max_length=100, null=True, blank=True)
    primary_care_physician = models.CharField(max_length=100)
    is_agreed = models.BooleanField(default=False)

    emergency_contact_name = models.CharField(max_length=20)
    emergency_contact_phone_number = models.CharField(max_length=19)
    emergency_contact_relation = models.CharField(max_length=30)

    insurance_primary = models.CharField(max_length=50)
    insurance_primary_id = models.CharField(max_length=50)
    insurance_primary_group = models.CharField(max_length=30)

    insurance_secondary = models.CharField(max_length=50)
    insurance_secondary_id = models.CharField(max_length=50)
    insurance_secondary_group = models.CharField(max_length=30)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "User detail"
        verbose_name_plural = "User details"

    def __str__(self):
        return self.user
