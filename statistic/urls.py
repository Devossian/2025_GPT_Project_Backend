from django.urls import path
from .views import CheckUsage

urlpatterns = [
    path('usage/', CheckUsage.as_view(), name='check-usage'),
]