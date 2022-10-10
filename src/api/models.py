from django.contrib.auth.models import AbstractUser
from django.db import models

from src.accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=50)
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.name)


class Room(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.category)


class Booking(models.Model):
    OPTIONS = (
        ('Option-1', 'Option-1'),
        ('Option-2', 'Option-2'),
    )
    CATEGORIES = (
        ('Company', 'Company'),
        ('Walking', 'Walking'),
    )
    created_on = models.DateTimeField(max_length=50, auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_rooms = models.PositiveIntegerField(default=None, null=True, blank=True)
    customer_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=50)
    customer_email = models.EmailField(max_length=50, null=True, blank=True, default=None)
    customer_cnic = models.CharField(max_length=50, null=True, blank=True, default=None)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='Walking')
    options = models.CharField(max_length=50, choices=OPTIONS, default='Option-1')
    rooms = models.ManyToManyField(Room)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    booking_base_64 = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.customer_name)


class BookingPayment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    payment = models.PositiveIntegerField(default=None, null=True, blank=True)
    payment_date_time = models.PositiveBigIntegerField(null=True, blank=True, default=None)
