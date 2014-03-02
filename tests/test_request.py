# coding=utf-8
from unittest import TestCase
from chinaapi.request import Request
from chinaapi.exceptions import ApiResponseError
import httpretty


BASE_URL = 'http://test/'


class TestBase(TestCase):
    URL = BASE_URL + 'oauth2/access_token'
    JSON_BODY = '{"access_token":"access_token","expires_in":60, "refresh_token":"refresh_token","uid":"uid"}'
    CONTENT_TYPE = 'text/json'

    def assertToken(self, token):
        self.assertEqual('access_token', token.access_token)
        self.assertEqual(60, token.expires_in)
        self.assertEqual('refresh_token', token.refresh_token)
        self.assertEqual('uid', token.uid)

    def _register_response(self, body='', status=200):
        httpretty.register_uri(httpretty.POST, self.URL, body, status=status, content_type=self.CONTENT_TYPE)


class RequestTest(TestBase):
    def setUp(self):
        self.request = Request()
        self.session = self.request._session

    @httpretty.activate
    def test_json_dict(self):
        self._register_response(self.JSON_BODY)
        response = self.session.post(self.URL)
        self.assertToken(response.json_dict())

    @httpretty.activate
    def test_jsonp_dict(self):
        self._register_response("jsonp(%s)" % self.JSON_BODY)
        response = self.session.post(self.URL)
        self.assertToken(response.jsonp_dict())

    @httpretty.activate
    def test_ApiResponseValueError(self):
        self._register_response('not json')
        with self.assertRaises(ApiResponseError):
            response = self.session.post(self.URL)
            response.json_dict()

    @httpretty.activate
    def test_NotExistApi(self):
        self._register_response(status=404)
        with self.assertRaises(ApiResponseError):
            response = self.session.post(self.URL)
            response.json_dict()

    @httpretty.activate
    def test_HTTPError(self):
        self._register_response(status=500)
        with self.assertRaises(ApiResponseError):
            response = self.session.post(self.URL)
            response.json_dict()
