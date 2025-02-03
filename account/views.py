from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from account.forms import EmailForm, SignupForm
from account.models import CustomUser
import account.utils

@extend_schema(
    summary="아이디 중복 확인",
    description="입력한 `username`이 사용 가능한지 확인합니다.",
    parameters=[
        OpenApiParameter(
            name="username",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description="사용자 아이디"
        ),
    ],
    responses={
        200: inline_serializer(
            name="UsernameAvailableResponse",
            fields={"message": serializers.CharField(help_text="사용 가능 여부 메시지")}
        ),
        400: inline_serializer(
            name="UsernameUnavailableResponse",
            fields={"message": serializers.CharField(help_text="사용 불가 메시지")}
        ),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 요구 비활성화
def check_username(request):
    username = request.GET.get("username")
    if account.utils.check_username(username):
        return Response({"message": "사용할 수 없는 아이디입니다"}, status=400)
    else:
        return Response({"message": "사용할 수 있는 아이디입니다"}, status=200)

@extend_schema(
    summary="이메일 인증 요청",
    description="입력한 이메일로 인증 요청을 보냅니다.",
    request=inline_serializer(
        name="SendEmailRequest",
        fields={"email": serializers.EmailField(help_text="이메일 주소")}
    ),
    responses={
        200: inline_serializer(
            name="SendEmailSuccessResponse",
            fields={"message": serializers.CharField(help_text="이메일 요청 성공 메시지")}
        ),
        400: inline_serializer(
            name="SendEmailFailureResponse",
            fields={"message": serializers.CharField(help_text="이메일 요청 실패 메시지")}
        ),
        500: inline_serializer(
            name="SendEmailServerErrorResponse",
            fields={"message": serializers.CharField(help_text="외부 인증서버 오류 메시지")}
        ),
    }
)
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


@extend_schema(
    summary="회원가입",
    description="이메일 인증 후 `username`, `password`, `email`을 입력하여 회원가입을 수행합니다.",
    request=inline_serializer(
        name="SignupRequest",
        fields={
            "username": serializers.CharField(help_text="사용자 아이디"),
            "password1": serializers.CharField(help_text="비밀번호"),
            "email": serializers.EmailField(help_text="이메일 주소"),
            "verification_code": serializers.CharField(help_text="이메일 인증 코드"),
        }
    ),
    responses={
        201: inline_serializer(
            name="SignupSuccessResponse",
            fields={"message": serializers.CharField(help_text="회원가입 성공 메시지")}
        ),
        400: inline_serializer(
            name="SignupFailureResponse",
            fields={
                "message": serializers.CharField(help_text="입력 오류 메시지"),
                "errors": serializers.DictField(help_text="입력 필드별 오류 상세 메시지"),
            }
        ),
        500: inline_serializer(
            name="SignupServerErrorResponse",
            fields={"message": serializers.CharField(help_text="회원가입 중 서버 오류 메시지")}
        ),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    data = request.data
    form = SignupForm(data)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        email = form.cleaned_data['email']
        verification_code = form.cleaned_data['verification_code']

        # 입력 코드 검증
        response = account.utils.validate_email_code(email, verification_code)

        if response.get("code") == 400:
            print(response.get("message"))
            return Response({"message": response.get("message")}, status=400)
        if response == 500:
            print("인증서버에 문제가 발생했습니다")
            return Response({"message": "인증서버에 문제가 발생했습니다"}, status=500)

        try:
            CustomUser.objects.create(
                username=username,
                email=email,
                password=make_password(password),  # 비밀번호 암호화
                balance=0.00
            )
            return Response({"message": "회원가입 성공"}, status=201)
        except Exception as e:
            print(e)
            if account.utils.clear_email(email) == 500:
                print("인증서버 장애로 이메일 인증 내역 삭제 실패")
                return Response({"message": "인증서버 장애로 문제가 발생했습니다. 관리자에게 문의해주세요"}, status=500)
            return Response({"message": "회원가입 중 문제가 발생했습니다."}, status=500)
    else:
        return Response({"message": "유효하지 않은 입력입니다", "errors": form.errors},status=400)

@extend_schema(
    summary="로그인",
    description="`username`과 `password`를 입력하여 로그인하고, 인증 토큰을 반환합니다.",
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "username": serializers.CharField(help_text="사용자 아이디"),
            "password": serializers.CharField(help_text="비밀번호"),
        }
    ),
    responses={
        200: inline_serializer(
            name="LoginSuccessResponse",
            fields={
                "message": serializers.CharField(help_text="로그인 성공 메시지"),
                "token": serializers.CharField(help_text="인증 토큰"),
            }
        ),
        400: inline_serializer(
            name="LoginFailureResponse",
            fields={"message": serializers.CharField(help_text="로그인 실패 메시지")}
        ),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data

    username = data.get('username')
    password = data.get('password')

    # 유저 인증
    user = authenticate(request, username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"message": "로그인 성공", "token": token.key}, status=200)
    else:
        return Response({"message": "아이디 또는 비밀번호가 잘못되었습니다."}, status=400)