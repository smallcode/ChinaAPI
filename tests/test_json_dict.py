# coding=utf-8
from unittest import TestCase
from chinaapi.utils import jsonDict


class JsonDictTest(TestCase):
    def test_loads(self):
        s = r'{"name":"smallcode","score":60}'
        json = jsonDict.loads(s)
        self.assertEqual('smallcode', json.name)
        self.assertEqual(60, json.score)
