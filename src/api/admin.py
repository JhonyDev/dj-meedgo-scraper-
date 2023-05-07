from django.contrib import admin

from . import models


class MedicineView(admin.ModelAdmin):
    list_display = ['pk', 'name', 'salt_name', 'price', 'platform', 'last_updated']


class MedicineCartView(admin.ModelAdmin):
    list_display = ['pk', 'user']


admin.site.register(models.Medicine, MedicineView)
admin.site.register(models.MedicineCart, MedicineCartView)
