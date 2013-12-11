# coding=utf-8
from unittest import TestCase
from chinaapi.utils.jsonDict import JsonDict, loads


class JsonDictTest(TestCase):
    def test_loads(self):
        json = loads(r'{"name":"foo","age":100}')
        self.assertEqual('foo', json.name)
        self.assertEqual(100, json.age)

    def test_JsonDict(self):
        json = JsonDict(name="foo", age=100)
        self.assertEqual('foo', json.name)
        self.assertEqual(100, json.age)
        json.age = 99
        self.assertEqual(99, json.age)

    def test_AttributeError(self):
        json = JsonDict(name="foo", age=100)
        with self.assertRaises(AttributeError):
            json.id
