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
        return str(self.name)


class Booking(models.Model):
    created_on = models.DateTimeField(max_length=50, auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    customer_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=50)
    payment = models.PositiveIntegerField(default=None, null=True, blank=True)
    payment_date = models.PositiveBigIntegerField(null=True, blank=True, default=None)
    rooms = models.ManyToManyField(Room)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.customer_name)
