from django.urls import path
from .views import PostGPTAPI

urlpatterns = [
    path('chat/send-message', PostGPTAPI.as_view(), name='post_gpt_api'),
]