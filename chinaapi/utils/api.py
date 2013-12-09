# coding=utf-8
import requests
from furl import furl
from requests.utils import default_user_agent
from chinaapi.utils import jsonDict
from chinaapi.utils.models import Token
from chinaapi.utils.exceptions import ApiNotExistError, ApiResponseError, EmptyRedirectUriError
from chinaapi import __version__, __title__


class Method(object):
    GET = 'GET'
    POST = 'POST'


class Parser(object):
    def parse_response(self, response):
        try:
            return jsonDict.loads(response.text)
        except ValueError, e:
            status_code = 200
            if response.status_code == status_code:
                message = response.text if response.text else str(e)
                raise ApiResponseError(response, status_code, message)
            else:
                raise ApiNotExistError(response)

    @staticmethod
    def parse_query_string(query_string):
        return dict([item.split('=') for item in query_string.split('&')])


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


class Client(Parser):
    def __init__(self, app):
        self.app = app
        self.token = Token()
        self._session = requests.session()
        self._session.headers['User-Agent'] = default_user_agent('%s/%s requests' % (__title__, __version__))

    def set_token(self, token):
        self.token = token

    @staticmethod
    def _isolated_files(queries, file_keys):
        for key in file_keys:
            if key in queries:
                return {key: queries.pop(key)}

    def _prepare_method(self, segments):
        return Method.POST

    def _prepare_url(self, segments, queries):
        raise NotImplementedError

    def _prepare_queries(self, queries):
        pass

    def _prepare_body(self, queries):
        data, files = {}, {}
        for k, v in queries.items():
            if hasattr(v, 'read'):  # 判断是否为文件
                files[k] = v
            else:
                data[k] = v
        return data, files

    def request(self, segments, **queries):
        url = self._prepare_url(segments, queries)
        method = self._prepare_method(segments)
        self._prepare_queries(queries)

        if method == Method.POST:
            data, files = self._prepare_body(queries)
            response = self._session.post(url, data=data, files=files)
        else:
            response = self._session.get(url, params=queries)

        return self.parse_response(response)

    def __getattr__(self, attr):
        return ClientWrapper(self, attr)


class OAuth(Parser):
    def __init__(self, app, url):
        self.app = app
        self.url = url
        self._session = requests.session()


class OAuth2(OAuth):
    def __init__(self, app, url):
        super(OAuth2, self).__init__(app, url)

    def _parse_token(self, response):
        return self.parse_response(response)

    def _get_authorize_url(self):
        return self.url + 'authorize'

    def _get_access_token_url(self):
        return self.url + 'access_token'

    def authorize(self, **kwargs):
        """  授权
        返回授权链接
        """
        if 'response_type' not in kwargs:
            kwargs['response_type'] = 'code'
        if 'redirect_uri' not in kwargs:
            kwargs['redirect_uri'] = self.app.redirect_uri
        kwargs['client_id'] = self.app.key
        url = furl(self._get_authorize_url()).set(args=kwargs).url
        if not kwargs['redirect_uri']:
            raise EmptyRedirectUriError(url)
        return url

    def access_token(self, **kwargs):
        """ 用code换取access_token
        请求参数说明：
            授权模式             所需参数
            authorization_code:  code 和 redirect_uri（可选）
            refresh_token:       refresh_token
            password:            username 和 password
            client_credentials:  无
        返回Token
        """
        if 'redirect_uri' not in kwargs:
            kwargs['redirect_uri'] = self.app.redirect_uri
        if 'code' in kwargs:
            grant_type = 'authorization_code'
        elif 'refresh_token' in kwargs:
            grant_type = 'refresh_token'
        elif 'username' in kwargs and 'password' in kwargs:
            grant_type = 'password'
        else:
            grant_type = 'client_credentials'
        kwargs.update(client_id=self.app.key, client_secret=self.app.secret, grant_type=grant_type)
        url = self._get_access_token_url()
        if grant_type == 'authorization_code' and not kwargs['redirect_uri']:
            raise EmptyRedirectUriError(url)
        response = self._session.post(url, data=kwargs)
        return self._parse_token(response)