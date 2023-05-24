from django.contrib import admin
from django.utils.html import format_html

from . import models


class MedicineView(admin.ModelAdmin):
    list_display = ['pk', 'Scrape', 'name', 'salt_name', 'price', 'discounted_price', 'is_available', 'platform',
                    'last_updated']
    search_fields = ['name', 'salt_name']
    list_filter = ['platform', 'is_available']

    def Scrape(self, obj):
        return format_html(f'<a class="button" href="/api/run-task/{obj.pk}/">Scrape</a>')

    Scrape.short_description = 'Scrape Again'

    # Override the change form buttons
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_custom_button'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


class MedicineCartView(admin.ModelAdmin):
    list_display = ['pk', 'user']


admin.site.register(models.Medicine, MedicineView)
admin.site.register(models.MedicineCart, MedicineCartView)
admin.site.register(models.OrderRequest)
admin.site.register(models.GrabUserBridge)
admin.site.register(models.MedicineCartBridge)
