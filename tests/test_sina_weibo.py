# coding=utf-8
from unittest import TestCase
from chinaapi.sina_weibo import ApiClient, ApiError
from chinaapi.utils.models import App, Token


class SinaWeiboTest(TestCase):
    def setUp(self):
        app = App('', '')
        token = Token('')
        self.client = ApiClient(app)
        self.client.set_access_token(token)

    def test_without_app_key(self):
        with self.assertRaises(ApiError) as cm:
            self.client.statuses.user_timeline()
        self.assertEqual(u'source paramter(appkey) is missing', cm.exception.msg)
