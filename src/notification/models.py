from django.db import models

from src.accounts.models import User


class Notification(models.Model):
    title = models.CharField(max_length=1000, null=True, default=None)
    description = models.CharField(max_length=1000, null=True, default=None)
    context = models.CharField(max_length=1000, null=True, default=None)
    user = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} - {self.context}'

    class Meta:
        ordering = ['-pk']
        indexes = [
            models.Index(fields=['user']),
        ]
