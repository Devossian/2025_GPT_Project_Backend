from django.test import TestCase
from unittest.mock import patch, Mock
from account.models import CustomUser
import os
from account.utils import (
    check_username,
)


class UtilsTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(username="test1", email="test1@chosun.ac.kr")
        CustomUser.objects.create(username="test2", email="test2@chosun.ac.kr")
        CustomUser.objects.create(username="test3", email="test3@naver.com")

    def test_username_in_use(self):
        self.assertTrue(check_username("test1"))
        self.assertFalse(check_username("unknownUser"))