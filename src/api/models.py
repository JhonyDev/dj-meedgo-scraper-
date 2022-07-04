from django.contrib.auth.models import AbstractUser
from django.db import models

from src.accounts.models import User


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
    sex = models.CharField(max_length=15, choices=SEX)
    name = models.CharField(max_length=50)
    ssn = models.CharField(max_length=25)
    address = models.TextField()
    zip_code = models.CharField(max_length=15)
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "User detail"
        verbose_name_plural = "User details"

    def __str__(self):
        return str(self.pk)


class Clinic(models.Model):
    title = models.CharField(default='', max_length=50)
    address = models.TextField(default='', max_length=50)

    manager = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="creator-admin+")

    class Meta:
        verbose_name = "Clinic"
        verbose_name_plural = "Clinics"

    def __str__(self):
        return str(self.pk)


class Slot(models.Model):
    date = models.DateField(null=False, blank=False)
    time = models.TimeField(null=False, blank=False)
    number_of_appointments = models.PositiveIntegerField()
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "Appointment Slot"
        verbose_name_plural = "Appointment Slots"

    def __str__(self):
        return str(self.pk)


class Appointment(models.Model):
    STATUS = (
        ('Cancelled', 'Cancelled'),
        ('Waiting', 'Waiting'),
        ('Complete', 'Complete'),
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, null=False, blank=False)
    status = models.CharField(default='Waiting', choices=STATUS, max_length=20)

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self):
        return str(self.pk)
