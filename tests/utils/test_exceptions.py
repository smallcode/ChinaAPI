# coding=utf-8
from unittest import TestCase
from chinaapi.utils.exceptions import ApiError, MutexApiParameters


class ExceptionTest(TestCase):
    def test_api_error(self):
        error = ApiError('http://request_url', 404, 'Request Api not found!')
        self.assertEqual('[404]: Request Api not found!, request: http://request_url', str(error))

    def test_api_error_with_sub(self):
        error = ApiError('http://request_url', 404, 'Request Api not found!', 1000, 'sub error msg')
        self.assertEqual('[404]: Request Api not found!, [1000]: sub error msg, request: http://request_url',
                         str(error))

    def test_mutex_api_parameters(self):
        error = MutexApiParameters(['pic', 'pic_url'])
        self.assertEqual(error.message, u'pic,pic_url参数只能选择其一')
