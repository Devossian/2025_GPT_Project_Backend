from django.urls import path
from . import views  # 해당 앱의 뷰 모듈 import

urlpatterns = [
    path('payment-session', views.create_payment_session, name='create_payment_session'),

]