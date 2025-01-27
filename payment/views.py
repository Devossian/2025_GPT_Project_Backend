import uuid

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from account.models import CustomUser
from payment.models import Payment
from django.core.cache import cache


@api_view(['POST'])
def create_payment_session(request):
    custom_key = request.user.custom_key
    order_id = uuid.uuid4()

    # order_id 중복 확인, 중복이 발생하지 않을 때까지 새로운 uuid 생성
    while Payment.objects.filter(order_id=order_id).exists():
        order_id = uuid.uuid4()

    print("custom_key:", custom_key, ",order_id:", order_id)

    # Redis에 저장
    amount = request.data.get("amount")
    redis_key = f"payment:{order_id}"
    cache.set(f"{redis_key}:custom_key", custom_key, timeout=6000)
    cache.set(f"{redis_key}:amount", amount, timeout=6000)

    stored_ck = cache.get(f"{redis_key}:custom_key")
    stored_am = cache.get(f"{redis_key}:amount")

    # print("redis_key: ", redis_key)
    # print(stored_ck, stored_am)

    return Response({"message": "결제정보가 저장되었습니다",
                     "custom_key": custom_key,
                     "order_id": order_id},
                    status=200)
