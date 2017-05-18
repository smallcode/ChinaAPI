# coding=utf-8
from unittest import TestCase
from chinaapi.renren.open import Client, App
from chinaapi.exceptions import ApiError


class RenRenTest(TestCase):
    """
    注释部分的测试需填写app_key,app_secret,access_token
    """

    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        self.client = Client(app)
        self.client.set_access_token('access_token')  # 填上取得的access_token
        self.uid = 334258249

    # def test_users_get(self):
    #     r = self.client.user.get(userId=self.uid)
    #     self.assertEqual(self.uid, r.id)

    def test_api_error(self):
        self.client.token.access_token = ''
        with self.assertRaises(ApiError) as cm:
            self.client.user.get(userId=self.uid)
        self.assertEqual('验证参数错误。', cm.exception.message)
