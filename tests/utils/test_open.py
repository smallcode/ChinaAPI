# coding=utf-8
from unittest import TestCase
import httpretty
from chinaapi.utils.open import ClientBase, OAuth2Base, Method, Token, App
from chinaapi.utils.exceptions import MissingRedirectUri
from test_api import BASE_URL, TestBase


class ApiClient(ClientBase):
    def __init__(self, app):
        super(ApiClient, self).__init__(app)

    def _prepare_url(self, segments, queries):
        return BASE_URL + '/'.join(segments)

    def _prepare_method(self, segments):
        if segments[-1] == 'get':
            return Method.GET
        return super(ApiClient, self)._prepare_method(segments)

    def _parse_response(self, response):
        return response


class NotImplementedClient(ClientBase):
    def __init__(self, app):
        super(NotImplementedClient, self).__init__(app)


class ApiOAuth2(OAuth2Base):
    def __init__(self, app):
        super(ApiOAuth2, self).__init__(app, 'http://test/oauth2/')


class RequestBase(TestBase):
    def setUp(self):
        self.app = App('key', 'secret', 'http://redirect_uri')


class ClientTest(RequestBase):
    GET_URL = BASE_URL + 'get'
    POST_URL = BASE_URL + 'post'

    def setUp(self):
        super(ClientTest, self).setUp()
        self.client = ApiClient(self.app)
        self.client.set_access_token('access_token', 60 * 60)

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


class NotImplementedClientTest(RequestBase):
    def setUp(self):
        super(NotImplementedClientTest, self).setUp()
        self.client = NotImplementedClient(self.app)

    def test_not_implemented_error(self):
        with self.assertRaises(NotImplementedError) as cm:
            self.client.not_implemented_error.get()


class OAuth2Test(RequestBase):
    def setUp(self):
        super(OAuth2Test, self).setUp()
        self.oauth2 = ApiOAuth2(self.app)
        self.oauth_url = 'http://test/oauth2/authorize?redirect_uri=http%3A%2F%2Fredirect_uri&response_type=code&client_id=key'

    def test_authorize(self):
        url = self.oauth2.authorize()
        self.assertEqual(self.oauth_url, url)

    def test_authorize_with_empty_redirect_uri(self):
        with self.assertRaises(MissingRedirectUri):
            self.oauth2.authorize(redirect_uri='')

    @httpretty.activate
    def test_access_token(self):
        self.register_access_token_uri()
        token = self.oauth2.access_token(code='code')
        self.assertToken(token)

    def test_access_token_with_empty_redirect_uri(self):
        with self.assertRaises(MissingRedirectUri):
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


class TokenTest(TestCase):
    def test_access_token(self):
        token = Token('token_string', 60 * 60)
        self.assertFalse(token.is_expires)

    def test_access_token_without_expired_at(self):
        token = Token('token_string')
        self.assertFalse(token.is_expires)

    def test_empty_access_token(self):
        token = Token('')
        self.assertTrue(token.is_expires)

    def test_expired_access_token(self):
        token = Token('token_string', - 60 * 60)
        self.assertTrue(token.is_expires)

    def test_set_expires_in(self):
        expires_in = 60 * 60
        token = Token('token_string', expires_in)
        self.assertAlmostEqual(expires_in, token.expires_in, -1)

    def test_get_attr(self):
        uid = 123
        token = Token(uid=uid)
        self.assertEqual(uid, token.uid)

    def test_get_not_exist_attr(self):
        token = Token()
        with self.assertRaises(KeyError):
            _ = token.not_exist_attr