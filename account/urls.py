from django.urls import path
from . import views

urlpatterns = [
    path('check-username', views.check_username, name='check_username'),

]