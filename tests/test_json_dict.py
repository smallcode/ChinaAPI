# coding=utf-8
from unittest import TestCase
from chinaapi.utils import jsonDict


class JsonDictTest(TestCase):
    def test_loads(self):
        s = r'{"name":"Michael","score":95}'
        json = jsonDict.loads(s)
        self.assertEqual('Michael', json.name)
        self.assertEqual(95, json.score)
