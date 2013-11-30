# coding=utf-8
from unittest import TestCase
from chinaapi.sina_weibo import APIClient, APIError


APP_KEY = ""
APP_SECRET = ""
CALLBACK_URL = ""
ACCESS_TOKEN = ""


class SinaWeiboTest(TestCase):
    def setUp(self):
        self.client = APIClient(APP_KEY, APP_SECRET, CALLBACK_URL)

    def test_without_app_key(self):
        with self.assertRaises(APIError) as cm:
            self.client.statuses.user_timeline.get()
        self.assertEqual(u'source paramter(appkey) is missing', cm.exception.error)
