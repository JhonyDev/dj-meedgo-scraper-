from django.contrib.auth.models import AbstractUser
from django.db import models

from src.accounts.models import User
from src.api.utils import PLATFORMS


class Medicine(models.Model):
    name = models.CharField(max_length=500)
    salt_name = models.CharField(max_length=500)
    price = models.PositiveIntegerField(null=True, blank=True, default=None)
    med_image = models.URLField(null=True, blank=True, default=None)
    platform = models.CharField(max_length=500, choices=PLATFORMS)
    dosage = models.PositiveIntegerField(null=True, blank=True, default=None, help_text="in Milligrams")

    def get_platform(self):
        return dict(PLATFORMS).get(self.platform)

    def __str__(self):
        return str(self.name)


class MedicineCart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicine, through='MedicineCartBridge', blank=True, null=True)

    def __str__(self):
        return str(self.pk)


class MedicineCartBridge(models.Model):
    medicine = models.ForeignKey(Medicine, null=True, blank=True, default=None, on_delete=models.CASCADE)
    medicine_card = models.ForeignKey(MedicineCart, null=True, blank=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)
