# coding=utf-8
from unittest import TestCase
from chinaapi.utils import parse_querystring

class UtilsTest(TestCase):
    def test_parse_querystring(self):
        r = parse_querystring("a=a&b=b")
        self.assertEqual(2, len(r))
        self.assertEqual('a', r['a'])
        self.assertEqual('b', r['b'])