# coding=utf-8
from unittest import TestCase
from chinaapi.decorators import retry


class DecoratorsTest(TestCase):
    n = 0

    @staticmethod
    def handle_error(exception):
        print(exception)

    def test_retry(self):
        @retry(3, hook=self.handle_error)
        def retry_me():
            self.n += 1
            raise Exception('exception in try %s' % self.n)

        self.assertRaises(Exception, retry_me)
        self.assertEqual(self.n, 3)







