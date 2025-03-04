from django.db import models
from account.models import CustomUser


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment')
    order_id = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_key = models.CharField(max_length=200)
    approved_at = models.DateTimeField()
