# coding=utf-8
import time
from requests.utils import default_user_agent
from .request import Request
from .exceptions import ApiError, MissingRedirectUri
from .utils import request_url
from .decorators import retry
from . import __version__, __title__

DEFAULT_RETRIES = 3


class Method(object):
    GET = 'GET'
    POST = 'POST'


class Token(object):
    def __init__(self, access_token=None, expires_in=None, refresh_token=None, **kwargs):
        """
        access_token：访问令牌
        expired_at：令牌到期日期，为timestamp格式
        expires_in：令牌剩余授权时间的秒数
        refresh_token：用于刷新令牌
        """
        self.access_token = access_token
        self.expired_at = None
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self._data = kwargs

    @staticmethod
    def _get_now():
        return int(time.time())

    def _get_expires_in(self):
        if self.expired_at:
            return self.expired_at - self._get_now()

    def _set_expires_in(self, expires_in):
        if expires_in:
            self.expired_at = int(expires_in) + self._get_now()

    expires_in = property(_get_expires_in, _set_expires_in)

    @property
    def is_expires(self):
        return not self.access_token or (self.expired_at is not None and self._get_now() > self.expired_at)

    def __getattr__(self, item):
        if item in self._data:
            return self._data[item]
        raise AttributeError


class App(object):
    def __init__(self, key='', secret='', redirect_uri=''):
        self.key = key
        self.secret = secret
        self.redirect_uri = redirect_uri


class ClientWrapper(object):
    def __init__(self, client, attr):
        """
        segments:用于保存API路径片段
        """
        self._client = client
        self._segments = [attr]

    def __call__(self, **kwargs):
        return self._client.request(self._segments, **kwargs)

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            self._segments.append(attr)
        return self


class ClientBase(Request):
    def __init__(self, app=App(), token=Token()):
        super(ClientBase, self).__init__()
        self.app = app
        self.token = token
        self._session.headers['User-Agent'] = default_user_agent('%s/%s requests' % (__title__, __version__))

    def set_access_token(self, access_token, expires_in=None):
        self.token = Token(access_token, expires_in)

    def _prepare_method(self, segments):
        return Method.POST

    def _prepare_url(self, segments, queries):
        raise NotImplementedError

    def _prepare_queries(self, queries):
        pass

    def _prepare_body(self, queries):
        results = ({}, {})
        for k, v in list(queries.items()):
            results[hasattr(v, 'read')][k] = v
        return results

    def _parse_response(self, response):
        return response

    def _is_retry_error(self, e):
        return False

    def prepare_request(self, segments, queries):
        url = self._prepare_url(segments, queries)
        method = self._prepare_method(segments)
        self._prepare_queries(queries)
        params, data, files = None, None, None
        if method == Method.POST:
            data, files = self._prepare_body(queries)
        else:
            params = queries
        return method, url, params, data, files

    def request(self, segments, **queries):
        method, url, params, data, files = self.prepare_request(segments, queries)

        def handle_error(e):
            if self._is_retry_error(e):
                if files:
                    for f in list(files.values()):
                        f.seek(0)
            else:
                raise e

        @retry(DEFAULT_RETRIES, ApiError, handle_error)
        def try_request():
            response = self._session.request(method, url, params=params, data=data, files=files)
            return self._parse_response(response)

        return try_request()

    def __getattr__(self, attr):
        return ClientWrapper(self, attr)


class OAuthBase(Request):
    def __init__(self, app=App()):
        super(OAuthBase, self).__init__()
        self.app = app


class OAuth2Base(OAuthBase):
    AUTH_URL = ''
    TOKEN_URL = ''

    def _parse_token(self, response):
        return response.json_dict()

    def authorize(self, **kwargs):
        """  授权
        返回授权链接
        """
        kwargs.setdefault('response_type', 'code')
        kwargs.setdefault('redirect_uri', self.app.redirect_uri)
        kwargs['client_id'] = self.app.key
        url = request_url(self.AUTH_URL, kwargs)
        if not kwargs['redirect_uri']:
            raise MissingRedirectUri(url)
        return url

    def access_token(self, **kwargs):
        """ 用code换取access_token，请求参数说明：
        授权模式             所需参数
        authorization_code:  code 和 redirect_uri（可选）
        refresh_token:       refresh_token
        password:            username 和 password
        client_credentials:  无
        @返回Token
        """
        if 'code' in kwargs:
            grant_type = 'authorization_code'
            kwargs.setdefault('redirect_uri', self.app.redirect_uri)
            if not kwargs['redirect_uri']:
                raise MissingRedirectUri(self.TOKEN_URL)
        elif 'refresh_token' in kwargs:
            grant_type = 'refresh_token'
        elif 'username' in kwargs and 'password' in kwargs:
            grant_type = 'password'
        else:
            grant_type = 'client_credentials'
        kwargs.update(client_id=self.app.key, client_secret=self.app.secret, grant_type=grant_type)
        response = self._session.post(self.TOKEN_URL, data=kwargs)
        return self._parse_token(response)

    def refresh_token(self, refresh_token, **kwargs):
        kwargs['refresh_token'] = refresh_token
        return self.access_token(**kwargs)
