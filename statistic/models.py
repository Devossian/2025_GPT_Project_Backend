from django.db import models
from account.models import CustomUser

# Create your models here.
class UsageRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='record')
    used_model = models.CharField(null=False)
    created_time = models.DateTimeField(auto_now_add=True)
    cost = models.IntegerField()