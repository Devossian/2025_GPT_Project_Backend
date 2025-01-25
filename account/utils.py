from account.models import CustomUser
import requests
import os

API_KEY = os.environ.get('UNIV_API_KEY')
BASE_URL = "https://univcert.com/api/v1"


def check_username(username):
    return CustomUser.objects.filter(username=username).exists()


def check_email(email):
    return CustomUser.objects.filter(email=email).exists()


def send_http_request(endpoint, payload):
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        print(response_data)

        return response_data
    except requests.exceptions.RequestException as e:
        print("send_http_request: 예외 발생, e = " + str(e))
        return 500


# 인증 이메일 발송
def send_email(email):
    payload = {
        "key": API_KEY,
        "email": email,
        "univName": "조선대학교",
        "univ_check": True
    }

    print(f"send_validation_email: {payload}")

    return send_http_request("certify", payload)