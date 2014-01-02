# coding=utf-8
from unittest import TestCase

import httpretty

from chinaapi.request import Request
from chinaapi.exceptions import ApiResponseError, NotExistApi


BASE_URL = 'http://test/'


class TestBase(TestCase):
    ACCESS_TOKEN_URL = BASE_URL + 'oauth2/access_token'
    JSON_BODY = '{"access_token":"access_token","expires_in":60, "refresh_token":"refresh_token","uid":"uid"}'
    CONTENT_TYPE = 'text/json'

    def assertToken(self, token):
        self.assertEqual('access_token', token.access_token)
        self.assertEqual(60, token.expires_in)
        self.assertEqual('refresh_token', token.refresh_token)
        self.assertEqual('uid', token.uid)

    def register_access_token_uri(self):
        httpretty.register_uri(httpretty.POST, self.ACCESS_TOKEN_URL, body=self.JSON_BODY,
                               content_type=self.CONTENT_TYPE)


class RequestTest(TestBase):
    HTTP404URL = BASE_URL + '404'
    NOT_JSON_RESPONSE_URL = BASE_URL + 'empty_response_uri'

    def setUp(self):
        self.request = Request()
        self.session = self.request._session

    def register_not_json_response_uri(self):
        httpretty.register_uri(httpretty.POST, self.NOT_JSON_RESPONSE_URL, body='error_text',
                               content_type=self.CONTENT_TYPE)

    def register_404_uri(self):
        httpretty.register_uri(httpretty.POST, self.HTTP404URL, body='error_text', status=404,
                               content_type=self.CONTENT_TYPE)

    @httpretty.activate
    def test_parse_response(self):
        self.register_access_token_uri()
        response = self.session.post(self.ACCESS_TOKEN_URL)
        self.assertToken(response.json_dict())

    @httpretty.activate
    def test_parse_not_json_response(self):
        self.register_not_json_response_uri()
        response = self.session.post(self.NOT_JSON_RESPONSE_URL)
        with self.assertRaises(ApiResponseError) as cm:
            response.json_dict()
        self.assertEqual('error_text', cm.exception.message)

    @httpretty.activate
    def test_parse_404_response(self):
        self.register_404_uri()
        response = self.session.post(self.HTTP404URL)
        with self.assertRaises(NotExistApi):
            response.json_dict()
