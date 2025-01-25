from django.test import TestCase
from unittest.mock import patch, Mock
from account.models import CustomUser
import os
from account.utils import (
    check_username,
    check_email,
    send_email,
)


class UtilsTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(username="test1", email="test1@chosun.ac.kr")
        CustomUser.objects.create(username="test2", email="test2@chosun.ac.kr")
        CustomUser.objects.create(username="test3", email="test3@naver.com")

    def test_username_in_use(self):
        self.assertTrue(check_username("test1"))
        self.assertFalse(check_username("unknownUser"))

    def test_email_in_use(self):
        self.assertTrue(check_email("test1@chosun.ac.kr"))
        self.assertFalse(check_email("unknown@chosun.ac.kr"))

    @patch("requests.post")
    def test_send_email_success(self, mock_post):
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # 이메일 인증 요청
        response = send_email("test1@chosun.ac.kr")
        self.assertEqual(response.get("success"), True)

        # post 요청이 다음 정보를 담고 1회 요청 되었는지 확인
        mock_post.assert_called_once_with(
            "https://univcert.com/api/v1/certify",
            json={
                "key": os.environ.get("UNIV_API_KEY"),
                "email": "test1@chosun.ac.kr",
                "univName": "조선대학교",
                "univ_check": True
            }
        )

    @patch("requests.post")
    def test_send_email_fail(self, mock_post):
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 400,
            "success": False,
            "message": "이미 완료된 요청입니다."
        }
        mock_post.return_value = mock_response

        # 이메일 인증 요청
        response = send_email("test1@chosun.ac.kr")
        self.assertEqual(response.get("success"), False)

        # post 요청이 다음 정보를 담고 1회 요청 되었는지 확인
        mock_post.assert_called_once_with(
            "https://univcert.com/api/v1/certify",
            json={
                "key": os.environ.get("UNIV_API_KEY"),
                "email": "test1@chosun.ac.kr",
                "univName": "조선대학교",
                "univ_check": True
            }
        )