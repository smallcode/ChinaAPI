# coding=utf-8
from unittest import TestCase
from chinaapi.renren import ApiClient
from chinaapi.utils.exceptions import ApiError
from chinaapi.utils.models import App, Token


class RenRenTest(TestCase):
    def setUp(self):
        app = App('', '')
        token = Token('')
        self.client = ApiClient(app)
        self.client.set_token(token)
        self.uid = 334258249

    def test_users_get(self):
        r = self.client.user.get(userId=self.uid)
        self.assertEqual(self.uid, r.id)

    def test_api_error(self):
        self.client.token.access_token = ''
        with self.assertRaises(ApiError) as cm:
            self.client.user.get(userId=self.uid)
        self.assertEqual(u'验证参数错误。', cm.exception.msg)
