from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from account.forms import EmailForm, SignupForm
from account.models import CustomUser
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
            account.utils.clear_email(email)  # 이메일 인증 내역 제거(제거 안할 시 이메일 인증이 다시 안됨)
            return Response({"message": "회원가입 성공"}, status=201)
        except Exception as e:
            print(e)
            if account.utils.clear_email(email) == 500:
                print("인증서버 장애로 이메일 인증 내역 삭제 실패")
                return Response({"message": "인증서버 장애로 문제가 발생했습니다. 관리자에게 문의해주세요"}, status=500)
            return Response({"message": "회원가입 중 문제가 발생했습니다."}, status=500)
    else:
        return Response({"message": "유효하지 않은 입력입니다", "errors": form.errors},status=400)


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
