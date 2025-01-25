from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from account.utils import check_email, check_username
from account.models import CustomUser

class EmailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email", )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if check_email(email):
            print("이미 사용중인 이메일입니다 : ", email)
            raise ValidationError("이미 사용중인 이메일입니다.")

        if not email.endswith("chosun.ac.kr") and not email.endswith("chosun.kr"):
            print("학교 이메일만 가입할 수 있습니다 :", email)
            raise ValidationError("학교 이메일만 가입할 수 있습니다.")

        return email


class SignupForm(UserCreationForm):
    verification_code = forms.CharField(label="인증번호", max_length=6)

    class Meta:
        model = CustomUser
        fields = ("username", "password1", "email")

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if check_username(username):
            print("clean_username: 이미 사용중인 아이디입니다.")
            raise ValidationError("이미 사용중인 아이디입니다.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if check_email(email):
            print("clean_email: 이미 사용중인 이메일입니다.")
            raise ValidationError("이미 사용중인 이메일입니다.")

        if not email.endswith("chosun.ac.kr") and not email.endswith("chosun.kr"):
            print("clean_email: 학교 이메일만 가입할 수 있습니다.")
            raise ValidationError("학교 이메일만 가입할 수 있습니다.")

        return email