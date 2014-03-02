# coding=utf-8
from unittest import TestCase
from chinaapi.qq.weibo.open import Client, App
from chinaapi.exceptions import ApiError


class QqWeiboTest(TestCase):
    """
    注释部分的测试需填写app_key,app_secret,access_token
    """

    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        self.openid = 'openid'  # 填上取得的openid
        self.client = Client(app)
        self.client.set_access_token('access_token')  # 填上取得的access_token
        self.client.openid = self.openid

    # def test_user_info(self):
    #     r = self.client.user.info()
    #     self.assertEqual(self.openid, r.openid)
    #
    # def test_t_upload_pic(self):
    #     with open('images/pic.jpg', 'rb') as pic:
    #         r = self.client.t.upload_pic(pic=pic, pic_type=2, clientip='220.181.111.85')  # clientip必填
    #     self.assertIsNotNone(r.imgurl)

    def test_api_error(self):
        self.client.openid = ''
        with self.assertRaises(ApiError) as cm:
            self.client.user.info()
        self.assertEqual('missing parameter', cm.exception.sub_message)

