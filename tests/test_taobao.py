# coding=utf-8
from unittest import TestCase
from chinaapi.taobao import APIClient, APIError


APP_KEY = ""
APP_SECRET = ""
CALLBACK_URL = ""
ACCESS_TOKEN = ""


class TaobaoTest(TestCase):
    def setUp(self):
        self.client = APIClient(APP_KEY, APP_SECRET)

    def test_without_app_key(self):
        with self.assertRaises(APIError) as cm:
            self.client.items_get(nicks='kamozi', fields='num_iid,title,price', page_no=1, page_size=2)
        self.assertEqual(u'Missing app key', cm.exception.msg)
