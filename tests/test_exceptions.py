# coding=utf-8
from unittest import TestCase
from chinaapi.exceptions import ApiError


class ExceptionTest(TestCase):
    def test_api_error(self):
        error = ApiError('http://request_url', 404, 'Request Api not found!')
        self.assertEqual('[404]: Request Api not found!, request: http://request_url', str(error))

    def test_api_error_with_sub(self):
        error = ApiError('http://request_url', 404, 'Request Api not found!', 1000, 'sub error msg')
        self.assertEqual('[404]: Request Api not found!, [1000]: sub error msg, request: http://request_url',
                         str(error))
