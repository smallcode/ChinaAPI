# coding=utf-8
from unittest import TestCase
from chinaapi.taobao import ApiClient
from chinaapi.utils.models import App


class TaobaoTest(TestCase):
    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        self.client = ApiClient(app)

    def test_tbk_shops_get(self):
        r = self.client.tbk.shops.get(cid=14, fields='user_id,seller_nick,shop_title,pic_url')
        self.assertEqual(40, len(r.tbk_shops_get_response.tbk_shops.tbk_shop))