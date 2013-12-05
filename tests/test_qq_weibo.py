# coding=utf-8
from unittest import TestCase
from chinaapi.qq_weibo import ApiClient
from chinaapi.utils.models import App, Token


# 返回text是unicode，设置默认编码为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class QqWeiboTest(TestCase):
    """
    测试时需填写app_key,app_secret,access_token
    """
    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token')  # 填上取得的access_token
        self.openid = 'openid'  # 填上取得的openid
        self.client = ApiClient(app)
        self.client.set_token(token)
        self.client.set_openid(self.openid)

    def test_user_info(self):
        r = self.client.user.info()
        self.assertEqual(self.openid, r.data.openid)

