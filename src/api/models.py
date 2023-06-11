from django.contrib.auth.models import AbstractUser
from django.db import models

from core.settings import PLATFORMS
from src.accounts.models import User


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.price:
            self.price = self.discounted_price

    def get_platform(self):
        return dict(PLATFORMS).get(self.platform)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-last_updated']


class MedicineCart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicine, through='MedicineCartBridge', blank=True, null=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


class OrderRequest(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Picked', 'Picked'),
        ('Dispatched', 'Dispatched'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    medicine_cart = models.ForeignKey(MedicineCart, on_delete=models.CASCADE)
    grabbed_by = models.ManyToManyField(User, through='GrabUserBridge', blank=True, null=True, related_name="+")
    order_status = models.CharField(max_length=25, null=True, blank=True, default='Pending', choices=STATUS)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


"""
 Many to Many Bridges
"""


class MedicineOfferBridge(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    medicine_cart_bridge = models.ForeignKey(
        'MedicineCartBridge', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    order_grab = models.ForeignKey('GrabUserBridge', on_delete=models.CASCADE, null=True, blank=True, default=None)
    offered_price = models.PositiveIntegerField(
        null=True, default=None, blank=True,
        help_text='Positive Integer expected. Mention amount in INR')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.medicine_cart_bridge = MedicineCartBridge.objects.filter(
        #     medicine=self.medicine, medicine_card=self.order_grab.order_request.medicine_cart).first()

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


class GrabUserBridge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    order_request = models.ForeignKey('OrderRequest', on_delete=models.CASCADE, null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


class MedicineCartBridge(models.Model):
    medicine = models.ForeignKey(Medicine, null=True, blank=True, default=None, on_delete=models.CASCADE)
    medicine_card = models.ForeignKey(MedicineCart, null=True, blank=True, default=None, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


"""======CHATTING-SEQUENCE======="""


class ConversationHistory(models.Model):
    receiving_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name="+")
    sending_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name="+")

    def get_target_user(self, current_user):
        if self.receiving_user != current_user:
            self.target_user = self.receiving_user
        else:
            self.target_user = self.sending_user
        return self.target_user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_user = None

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


class Message(models.Model):
    conversation_history = models.ForeignKey(
        ConversationHistory, on_delete=models.CASCADE, null=True, blank=True, default=None)
    message = models.TextField(max_length=500)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name="+")
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-pk']


class UserRating(models.Model):
    given_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pharmacist+')
    given_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user+')
    rating = models.PositiveIntegerField(default=None, null=True)
    comment = models.TextField(null=True, default=None)
