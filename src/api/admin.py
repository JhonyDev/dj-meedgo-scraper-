from django.contrib import admin

from . import models


class MedicineView(admin.ModelAdmin):
    list_display = ['pk', 'name', 'price', 'med_image', 'platform', 'dosage']


class MedicineCartView(admin.ModelAdmin):
    list_display = ['pk', 'user']


admin.site.register(models.Medicine, MedicineView)
admin.site.register(models.MedicineCart, MedicineCartView)
