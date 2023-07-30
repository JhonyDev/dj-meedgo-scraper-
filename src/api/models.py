from django.contrib.auth.models import AbstractUser
from django.db import models

from core.settings import PLATFORMS


class Medicine(models.Model):
    name = models.CharField(max_length=1000, null=True, default=None)
    salt_name = models.TextField(null=True, default=None)
    price = models.FloatField(null=True, blank=True, default=None)
    discounted_price = models.FloatField(null=True, blank=True, default=None)
    med_image = models.URLField(null=True, blank=True, default=None)
    platform = models.CharField(max_length=500, choices=PLATFORMS)
    dosage = models.PositiveIntegerField(null=True, blank=True, default=None, help_text="in Milligrams")
    med_url = models.URLField(null=True, blank=True, default=None, unique=True)
    is_available = models.BooleanField(default=True)
    last_updated = models.DateTimeField(default=None, null=True, blank=True)
    med_count = models.PositiveIntegerField(default=None, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.price:
            self.price = self.discounted_price
        self.med_count = 0

    def get_platform(self):
        return dict(PLATFORMS).get(self.platform)

    def __str__(self):
        return f'{self.name} - {self.salt_name}'

    class Meta:
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['name', 'salt_name']),
            models.Index(fields=['price', 'discounted_price']),
        ]
