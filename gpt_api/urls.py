from django.urls import path
from .views import PostGPTAPI

urlpatterns = [
    path('post-gpt-api', PostGPTAPI.as_view(), name='post_gpt_api'),
]