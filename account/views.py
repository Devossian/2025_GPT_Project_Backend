from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from account.forms import EmailForm
import account.utils


@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 요구 비활성화
def check_username(request):
    username = request.GET.get("username")
    if account.utils.check_username(username):
        return Response({"message": "사용할 수 없는 아이디입니다"}, status=400)
    else:
        return Response({"message": "사용할 수 있는 아이디입니다"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])  # 인증 요구 비활성화
def send_email(request):
    data = request.data
    form = EmailForm(data)
    if form.is_valid():
        email = form.cleaned_data['email']
        response = account.utils.send_email(email)

        if response.get("success"):
            return Response({"message": "이메일이 성공적으로 요청되었습니다"}, status=200)
        if response.get("code") == 400:
            return Response({"message": response.get("message")}, status=400)

        return Response({"message": "외부 인증서버에서 오류가 발생했습니다"}, status=500)
    else:
        return Response({"message": form.errors['email'][0]}, status=400)