import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    custom_key = models.UUIDField(default=uuid.uuid4)
    balance = models.DecimalField(
        max_digits=12,  # 최대 자리수 (10억까지 저장 가능)
        decimal_places=2,  # 소수점 자리수 (예: 소수점 둘째 자리까지)
        default=0.00  # 초기값
    )

    def __str__(self):
        return self.username