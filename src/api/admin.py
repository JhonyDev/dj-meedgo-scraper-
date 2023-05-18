from django.contrib import admin

from . import models


class MedicineView(admin.ModelAdmin):
    list_display = ['pk', 'name', 'salt_name', 'price', 'discounted_price', 'is_available', 'platform', 'last_updated']
    search_fields = ['name', 'salt_name']
    list_filter = ['platform', 'is_available']


class MedicineCartView(admin.ModelAdmin):
    list_display = ['pk', 'user']


admin.site.register(models.Medicine, MedicineView)
admin.site.register(models.MedicineCart, MedicineCartView)
admin.site.register(models.OrderRequest)
admin.site.register(models.GrabUserBridge)
admin.site.register(models.MedicineCartBridge)
