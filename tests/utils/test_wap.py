# coding=utf-8
from unittest import TestCase
from chinaapi.utils.wap import ClientBase


class ApiClient(ClientBase):
    def __init__(self):
        super(ApiClient, self).__init__()


class ClientTest(TestCase):
    def test_init(self):
        client = ApiClient()


