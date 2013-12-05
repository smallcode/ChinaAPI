# coding=utf-8
from unittest import TestCase
from chinaapi.sina_weibo import ApiClient
from chinaapi.utils.models import App, Token


class SinaWeiboTest(TestCase):
    """
    测试时需填写app_key,app_secret,access_token
    """
    def setUp(self):
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token', 1390850926)  # 填上取得的access_token
        self.client = ApiClient(app)
        self.client.set_token(token)
        self.uid = 3856184660

    def test_users_show(self):
        r = self.client.users.show(uid=self.uid)
        self.assertEqual(self.uid, r.id)

    def test_statuses_upload_url_text(self):
        url = 'http://tp1.sinaimg.cn/1265020392/180/40030782486/1'
        r = self.client.statuses.upload_url_text(status=u'发布的内容', url=url)
        self.assertIsNotNone(r.id)
        self.assertEqual(self.uid, r.user.id)
        self.client.statuses.destroy(id=r.id)

    def test_statuses_upload(self):
        pic = open('fixtures/images/pic.jpg', 'rb')
        r = self.client.statuses.upload(status=u'发布的内容', pic=pic)
        self.assertIsNotNone(r.id)
        self.assertEqual(self.uid, r.user.id)
        self.client.statuses.destroy(id=r.id)

    def test_upload_pic(self):
        pic = open('fixtures/images/pic.jpg', 'rb')
        r = self.client.statuses.upload_pic(pic=pic)
        self.assertIsNotNone(r.pic_id)
