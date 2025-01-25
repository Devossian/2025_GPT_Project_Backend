from account.models import CustomUser
import os

API_KEY = os.environ.get('UNIV_API_KEY')
BASE_URL = "https://univcert.com/api/v1"


def check_username(username):
    return CustomUser.objects.filter(username=username).exists()


def check_email(email):
    return CustomUser.objects.filter(email=email).exists()