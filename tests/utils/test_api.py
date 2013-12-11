# coding=utf-8
from unittest import TestCase
import httpretty
import requests
from chinaapi.utils.api import Client, OAuth2, Parser, Method
from chinaapi.utils.exceptions import EmptyRedirectUriError, ApiResponseError, ApiNotExistError
from chinaapi.utils.models import App, Token


BASE_URL = 'http://test/'


class ApiClient(Client, Parser):
    def __init__(self, app):
        super(ApiClient, self).__init__(app)

    def _prepare_url(self, segments, queries):
        return BASE_URL + '/'.join(segments)

    def _prepare_method(self, segments):
        if segments[-1] == 'get':
            return Method.GET
        return super(ApiClient, self)._prepare_method(segments)

    def parse_response(self, response):
        return response


class NotImplementedClient(Client):
    def __init__(self, app):
        super(NotImplementedClient, self).__init__(app)


class ApiOAuth2(OAuth2):
    def __init__(self, app):
        super(ApiOAuth2, self).__init__(app, 'http://test/oauth2/')


class TestBase(TestCase):
    ACCESS_TOKEN_URL = BASE_URL + 'oauth2/access_token'
    JSON_BODY = '{"access_token":"access_token","expires_in":60, "refresh_token":"refresh_token","uid":"uid"}'
    CONTENT_TYPE = 'text/json'

    def setUp(self):
        self.app = App('key', 'secret', 'http://redirect_uri')

    def assertToken(self, token):
        self.assertEqual('access_token', token.access_token)
        self.assertEqual(60, token.expires_in)
        self.assertEqual('refresh_token', token.refresh_token)
        self.assertEqual('uid', token.uid)

    def register_access_token_uri(self):
        httpretty.register_uri(httpretty.POST, self.ACCESS_TOKEN_URL, body=self.JSON_BODY,
                               content_type=self.CONTENT_TYPE)


class ParserTest(TestBase):
    HTTP404URL = BASE_URL + '404'
    NOT_JSON_RESPONSE_URL = BASE_URL + 'empty_response_uri'

    def setUp(self):
        self.parser = Parser()

    def register_not_json_response_uri(self):
        httpretty.register_uri(httpretty.POST, self.NOT_JSON_RESPONSE_URL, body='error_text',
                               content_type=self.CONTENT_TYPE)

    def register_404_uri(self):
        httpretty.register_uri(httpretty.POST, self.HTTP404URL, body='error_text', status=404,
                               content_type=self.CONTENT_TYPE)

    def test_parse_query_string(self):
        r = self.parser.parse_query_string("a=a&b=b")
        self.assertEqual(2, len(r))
        self.assertEqual('a', r['a'])
        self.assertEqual('b', r['b'])

    @httpretty.activate
    def test_parse_response(self):
        self.register_access_token_uri()
        response = requests.post(self.ACCESS_TOKEN_URL)
        token = self.parser.parse_response(response)
        self.assertToken(token)

    @httpretty.activate
    def test_parse_not_json_response(self):
        self.register_not_json_response_uri()
        response = requests.post(self.NOT_JSON_RESPONSE_URL)
        with self.assertRaises(ApiResponseError) as cm:
            self.parser.parse_response(response)
        self.assertEqual('error_text', cm.exception.message)

    @httpretty.activate
    def test_parse_404_response(self):
        self.register_404_uri()
        response = requests.post(self.HTTP404URL)
        with self.assertRaises(ApiNotExistError):
            self.parser.parse_response(response)


class ClientTest(TestBase):
    GET_URL = BASE_URL + 'get'
    POST_URL = BASE_URL + 'post'

    def setUp(self):
        super(ClientTest, self).setUp()
        self.token = Token('access_token', 1390850926, uid=123)
        self.client = ApiClient(self.app)
        self.client.set_token(self.token)

    def register_get_uri(self):
        httpretty.register_uri(httpretty.GET, self.GET_URL, body=self.JSON_BODY, content_type=self.CONTENT_TYPE)

    def register_post_uri(self):
        httpretty.register_uri(httpretty.POST, self.POST_URL, body=self.JSON_BODY, content_type=self.CONTENT_TYPE)

    def assertPost(self, response):
        self.assertEqual(self.POST_URL, response.url)
        self.assertEqual(self.JSON_BODY, response.text)
        self.assertEqual(Method.POST, response.request.method)

    @httpretty.activate
    def test_get(self):
        self.register_get_uri()
        r = self.client.get()
        self.assertEqual(self.GET_URL, r.url)
        self.assertEqual(self.JSON_BODY, r.text)
        self.assertEqual(Method.GET, r.request.method)

    @httpretty.activate
    def test_post(self):
        self.register_post_uri()
        response = self.client.post(id=123, name='name')
        self.assertPost(response)
        self.assertEqual('name=name&id=123', response.request.body)

    @httpretty.activate
    def test_post_with_pic(self):
        self.register_post_uri()
        with open('images/pic.jpg', 'rb') as pic:
            response = self.client.post(pic=pic, id=123)
            self.assertPost(response)
            self.assertTrue('multipart/form-data' in response.request.headers['Content-Type'])

    def test_isolated_files(self):
        with open('images/pic.jpg', 'rb') as pic:
            queries = dict(pic=pic, id=123)
            files = self.client._isolated_files(queries, ['pic'])
            self.assertEqual(1, len(files))
            self.assertEqual(pic, files['pic'])
            self.assertEqual(1, len(queries))
            self.assertEqual(123, queries['id'])


class NotImplementedClientTest(TestBase):
    def setUp(self):
        super(NotImplementedClientTest, self).setUp()
        self.client = NotImplementedClient(self.app)

    def test_not_implemented_error(self):
        with self.assertRaises(NotImplementedError) as cm:
            self.client.not_implemented_error.get()


class OAuth2Test(TestBase):
    def setUp(self):
        super(OAuth2Test, self).setUp()
        self.oauth2 = ApiOAuth2(self.app)
        self.oauth_url = 'http://test/oauth2/authorize?redirect_uri=http://redirect_uri&response_type=code&client_id=key'

    def test_authorize(self):
        url = self.oauth2.authorize()
        self.assertEqual(self.oauth_url, url)

    def test_authorize_with_empty_redirect_uri(self):
        with self.assertRaises(EmptyRedirectUriError):
            self.oauth2.authorize(redirect_uri='')

    @httpretty.activate
    def test_access_token(self):
        self.register_access_token_uri()
        token = self.oauth2.access_token(code='code')
        self.assertToken(token)

    def test_access_token_with_empty_redirect_uri(self):
        with self.assertRaises(EmptyRedirectUriError):
            self.oauth2.access_token(code='code', redirect_uri='')

    @httpretty.activate
    def test_refresh_token(self):
        self.register_access_token_uri()
        token = self.oauth2.access_token(refresh_token='code')
        self.assertToken(token)

    @httpretty.activate
    def test_password(self):
        self.register_access_token_uri()
        token = self.oauth2.access_token(username='username', password='password')
        self.assertToken(token)

    @httpretty.activate
    def test_credentials(self):
        self.register_access_token_uri()
        token = self.oauth2.access_token()
        self.assertToken(token)

