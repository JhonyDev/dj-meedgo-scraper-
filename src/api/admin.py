from django.contrib import admin

from . import models


class ClinicView(admin.ModelAdmin):
    list_display = ['pk', 'title', 'address', 'manager', 'creator']
    search_fields = ['title', 'address']


admin.site.register(models.UserDetail)
admin.site.register(models.Appointment)
admin.site.register(models.Slot)
admin.site.register(models.Clinic, ClinicView)
