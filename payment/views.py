import uuid

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from account.models import CustomUser
from payment.models import Payment


@api_view(['POST'])
def create_payment_session(request):
    custom_key = request.user.custom_key
    order_id = uuid.uuid4()

    # order_id 중복 확인, 중복이 발생하지 않을 때까지 새로운 uuid 생성
    while Payment.objects.filter(order_id=order_id).exists():
        order_id = uuid.uuid4()

    print("custom_key:", custom_key, ",order_id:", order_id)

    # TODO Redis에 저장

    return Response({"message": "결제정보가 저장되었습니다",
                     "custom_key": custom_key,
                     "order_id": order_id},
                    status=200)
