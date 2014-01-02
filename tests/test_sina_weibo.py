# coding=utf-8
from unittest import TestCase
from chinaapi.sina.weibo.open import Client
from chinaapi.exceptions import ApiError


class SinaWeiboTest(TestCase):
    """
    注释部分的测试需填写access_token
    """

    def setUp(self):
        self.client = Client()
        self.client.set_access_token('access_token')  # 填上取得的access_token
        self.uid = 3856184660

    # def test_users_show(self):
    #     r = self.client.users.show(uid=self.uid)
    #     self.assertEqual(self.uid, r.id)
    #
    # def test_statuses_upload(self):
    #     with open('images/pic.jpg', 'rb') as pic:
    #         r = self.client.statuses.upload(status=u'发布的内容', pic=pic)
    #         self.assertIsNotNone(r.id)
    #         self.assertEqual(self.uid, r.user.id)
    #         self.client.statuses.destroy(id=r.id)

    def test_not_exist_api(self):
        with self.assertRaises(ApiError) as cm:
            self.client.not_exist_api.get()
        self.assertEqual('Request Api not found!', cm.exception.message)
