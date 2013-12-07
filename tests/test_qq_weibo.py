# coding=utf-8
from unittest import TestCase
from chinaapi.qq_weibo import ApiClient
from chinaapi.utils.exceptions import ApiError, ApiNotExistError, ApiInvalidError
from chinaapi.utils.models import App, Token


# 返回text是unicode，设置默认编码为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class QqWeiboTest(TestCase):
    """
    注释部分的测试需填写app_key,app_secret,access_token
    """
    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token')  # 填上取得的access_token
        self.openid = 'openid'  # 填上取得的openid
        self.client = ApiClient(app)
        self.client.set_token(token)
        self.client.set_openid(self.openid)

    # def test_user_info(self):
    #     r = self.client.user.info()
    #     self.assertEqual(self.openid, r.openid)
    #
    # def test_t_upload_pic(self):
    #     with open('fixtures/images/pic.jpg', 'rb') as pic:
    #         r = self.client.t.upload_pic(pic=pic, pic_type=2, clientip='220.181.111.85')  # clientip必填
    #     self.assertIsNotNone(r.imgurl)

    def test_not_exist_api(self):
        with self.assertRaises(ApiNotExistError):
            self.client.not_exist_api.get()

    def test_invalid_api(self):
        with self.assertRaises(ApiInvalidError):
            self.client.too.many.segments.get()

    def test_api_error(self):
        self.client.openid = ''
        with self.assertRaises(ApiError) as cm:
            self.client.user.info()
        self.assertEqual('missing parameter', cm.exception.sub_message)

