from django import forms
from django.core.exceptions import ValidationError
from account.utils import check_email
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