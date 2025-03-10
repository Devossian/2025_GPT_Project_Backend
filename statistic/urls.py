from django.urls import path
from .views import CheckUsage, CheckCharge

urlpatterns = [
    path('usage', CheckUsage.as_view(), name='check-usage'),
    path('charge', CheckCharge.as_view(), name='check-charge'),
]