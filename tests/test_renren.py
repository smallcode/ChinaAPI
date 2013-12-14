# coding=utf-8
from unittest import TestCase
from chinaapi.renren.open import Client
from chinaapi.utils.exceptions import ApiError, NotExistApi
from chinaapi.utils.open import Token, App


class RenRenTest(TestCase):
    """
    注释部分的测试需填写app_key,app_secret,access_token
    """

    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token')  # 填上取得的access_token
        self.client = Client(app)
        self.client.set_token(token)
        self.uid = 334258249

    # def test_users_get(self):
    #     r = self.client.user.get(userId=self.uid)
    #     self.assertEqual(self.uid, r.id)

    def test_api_error(self):
        self.client.token.access_token = ''
        with self.assertRaises(ApiError) as cm:
            self.client.user.get(userId=self.uid)
        self.assertEqual(u'验证参数错误。', cm.exception.message)

    def test_not_exist_api(self):
        with self.assertRaises(NotExistApi):
            self.client.not_exist_api.get()
