# coding=utf-8
from unittest import TestCase
from chinaapi.utils import jsonDict


class JsonDictTest(TestCase):
    def test_loads(self):
        s = r'{"name":"foo","age":100}'
        json = jsonDict.loads(s)
        self.assertEqual('foo', json.name)
        self.assertEqual(100, json.age)
