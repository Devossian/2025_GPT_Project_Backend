import base64, requests, uuid, os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from payment.models import Payment
from django.core.cache import cache

secret_key = os.environ.get('TOSS_SECRET_KEY')


@api_view(['POST'])
def create_payment_session(request):
    custom_key = request.user.custom_key
    amount = request.data.get("amount")

    if amount is None:
        Response({"message": "금액이 입력되지 않았습니다"}, status=400)

    order_id = uuid.uuid4()

    # order_id 중복 확인, 중복이 발생하지 않을 때까지 새로운 uuid 생성
    while Payment.objects.filter(order_id=order_id).exists():
        order_id = uuid.uuid4()

    print("custom_key:", custom_key, ",order_id:", order_id)

    # Redis에 저장
    redis_key = f"payment:{order_id}"

    cache.set(redis_key, amount, timeout=6000)

    return Response({"message": "결제정보가 저장되었습니다",
                     "custom_key": custom_key,
                     "order_id": order_id},
                    status=200)


# 결제 승인 호출하는 함수
# @docs https://docs.tosspayments.com/guides/v2/payment-widget/integration#3-결제-승인하기
@api_view(['GET'])
def confirm(request):
    orderId = request.GET.get('orderId')
    amount = request.GET.get('amount')
    paymentKey = request.GET.get('paymentKey')

    if orderId is None or amount is None or paymentKey is None:
        return Response({"message": "요청 정보가 부족합니다"}, status=400)

    success, message = validate_payment(orderId, amount)
    if not success:
        return Response({"message": message}, status=400)

    url = "https://api.tosspayments.com/v1/payments/confirm"
    headers = create_headers()
    params = {
        "orderId": orderId,
        "amount": amount,
        "paymentKey": paymentKey
    }

    resjson, status_code = send_payment_request(url, params, headers)
    return handle_response(request, resjson, status_code)


# API 요청에 헤더를 생성하는 함수
def create_headers():
    # 토스페이먼츠 API는 시크릿 키를 사용자 ID로 사용하고, 비밀번호는 사용하지 않습니다.
    # 비밀번호가 없다는 것을 알리기 위해 시크릿 키 뒤에 콜론을 추가합니다.
    # @docs https://docs.tosspayments.com/reference/using-api/authorization#%EC%9D%B8%EC%A6%9D
    userpass = f"{secret_key}:"
    encoded_u = base64.b64encode(userpass.encode()).decode()
    return {
        "Authorization": f"Basic {encoded_u}",
        "Content-Type": "application/json"
    }


# API 요청을 호출하고 응답 핸들링하는 함수
def send_payment_request(url, params, headers):
    response = requests.post(url, json=params, headers=headers)
    return response.json(), response.status_code


# 성공 및 실패 처리 함수
def handle_response(request, resjson, status_code):
    user = request.user
    if status_code == 200:
        try:
            # 성공 결제 정보 저장
            Payment.objects.create(
                user=user,
                order_id=resjson.get("orderId"),
                amount=resjson.get("totalAmount"),
                payment_key=resjson.get("paymentKey"),
                approved_at=resjson.get("approvedAt"),
            )

            return Response({"message": "결제 승인에 성공했습니다"}, status=200)
        except Exception as e:
            print("결제 정보 저장 실패: paymentKey: ", resjson.get("paymentKey"))
            print("결제 정보 저장 실패: order_id: ", resjson.get("orderId"))
            print("결제 정보 저장 실패: user: ", user)
            print(e)
            return Response({
                "message": "결제 정보 저장에 실패하여 승인을 실패했습니다"}, status=500)
    else:
        return Response({
            "code": resjson.get("code"),
            "message": resjson.get("message"),
        }, status=400)


def validate_payment(orderId, amount):
    # TODO 1. 데이터가 redis에 없는 경우
    # TODO 2. redis 데이터와 amount가 일치하지 않는 경우

    cached_data = cache.get(f"payment:{orderId}")
    if cached_data is None:
        return False, "결제 정보가 유효하지 않습니다"
    if int(cached_data) != int(amount):
        return False, "결제 금액이 일치하지 않습니다"
    return True, "결제가 유효합니다"




