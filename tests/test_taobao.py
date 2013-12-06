# coding=utf-8
from unittest import TestCase
from chinaapi.taobao import ApiClient
from chinaapi.utils.exceptions import ApiError
from chinaapi.utils.models import App


class TaobaoTest(TestCase):
    """
    # 使用这里公开的app：
    https://github.com/jimboybo/itaobox/blob/083e66bdce899ff8b9ea8be5fd9280529c4ee216/u/system/config/app_config.php
    注意：不同的app会有不同的权限，所以测试如果不成功，有可能是权限不足（详细原因可以查看返回的ApiError错误信息）
    """
    def setUp(self):
        app = App('21532233', '1d5f36785a0bfb84952a69c5dd3203fd')
        self.client = ApiClient(app)

    def test_itemcats_get(self):
        r = self.client.itemcats.get(cids=14)
        self.assertEqual(14, r.itemcats_get_response.item_cats.item_cat[0].cid)

    def test_shopcats_list_get(self):
        r = self.client.shopcats.list.get(cids=14)
        self.assertEqual(68, len(r.shopcats_list_get_response.shop_cats.shop_cat))

    def test_shop_get(self):
        r = self.client.shop.get(nick='kamozi', fields='sid,cid,title,nick,created')
        self.assertEqual(279839, r.shop_get_response.shop.sid)

    def test_not_exist_api(self):
        with self.assertRaises(ApiError) as cm:
            r = self.client.shop123.get()
        self.assertEqual('Invalid method', cm.exception.message)