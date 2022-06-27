from django.contrib import admin

from . import models

admin.site.register(models.UserDetail)
admin.site.register(models.Appointment)
admin.site.register(models.Slot)
admin.site.register(models.Clinic)
