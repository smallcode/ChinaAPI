# coding=utf-8
from unittest import TestCase
from chinaapi.qq_weibo import APIClient, OAuth2Handler, APIError


# 返回text是unicode，设置默认编码为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# 换成你的 APPKEY
APP_KEY = ""
APP_SECRET = ""
CALLBACK_URL = ""
ACCESS_TOKEN = ""
OPENID = ""


class QQWeiboTest(TestCase):
    def setUp(self):
        oauth = OAuth2Handler()
        oauth.set_app_key_secret(APP_KEY, APP_SECRET, CALLBACK_URL)
        oauth.set_token(ACCESS_TOKEN)
        oauth.set_openid(OPENID)
        self.client = APIClient(oauth)

    def test_without_app_key(self):
        with self.assertRaises(APIError) as cm:
            r = self.client.get.t__show(format="json", id=301041004850688)
        self.assertEqual(u'missing parameter', cm.exception.result.msg)
