# coding=utf-8
from unittest import TestCase
from chinaapi.utils import parse_querystring


class UtilsTest(TestCase):
    def test_parse_querystring(self):
        r = parse_querystring("http://test.com?foo=bar&n=1")
        self.assertEqual(2, len(r))
        self.assertEqual(r['foo'], 'bar')
        self.assertEqual( r['n'], '1')