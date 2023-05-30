from django.contrib import admin
from django.utils.html import format_html

from . import models
from .utils import get_platform_dict, FLIPCART


class MedicineView(admin.ModelAdmin):
    list_display = ['pk', 'Scrape', 'scrape_all_medicines_in', 'name', 'salt_name', 'price', 'discounted_price',
                    'is_available',
                    'platform',
                    'last_updated']
    search_fields = ['name', 'salt_name']
    list_filter = ['platform', 'is_available']

    def Scrape(self, obj):
        if obj.platform == get_platform_dict()[FLIPCART]:
            return format_html(f'<a class="button" disabled>Scrape</a>')
        return format_html(f'<a class="button" href="/api/run-task/{obj.pk}/">Scrape</a>')

    def scrape_all_medicines_in(self, obj):
        if obj.platform == get_platform_dict()[FLIPCART]:
            return format_html(f'<a class="button" disabled>Scrape All</a>')
        return format_html(f'<a class="button" href="/api/run-task/{obj.pk}/all/">{obj.get_platform()}</a>')

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
