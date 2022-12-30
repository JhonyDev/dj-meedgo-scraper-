from django.contrib import admin

from . import models

admin.site.register(models.Service)
admin.site.register(models.Category)
admin.site.register(models.Room)
admin.site.register(models.Booking)
admin.site.register(models.BookingPayment)
