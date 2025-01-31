from django.urls import path
from .views import PostGPTAPI

urlpatterns = [
    path('send-message', PostGPTAPI.as_view(), name='send-message'),
]