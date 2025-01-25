from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import account.utils


@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 요구 비활성화
def check_username(request):
    username = request.GET.get("username")
    if account.utils.check_username(username):
        return Response({"message": "사용할 수 없는 아이디입니다"}, status=400)
    else:
        return Response({"message": "사용할 수 있는 아이디입니다"}, status=200)