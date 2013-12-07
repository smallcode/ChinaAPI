# coding=utf-8
import requests
from requests.utils import default_user_agent
from chinaapi.utils import jsonDict
from chinaapi.utils.models import Token
from chinaapi.utils.exceptions import ApiNotExistError, ApiResponseError
from chinaapi import __version__, __title__


class Method(object):
    GET = 'GET'
    POST = 'POST'


class Parser(object):
    def parse(self, response):
        try:
            return jsonDict.loads(response.text)
        except ValueError, e:
            status_code = 200
            if response.status_code == status_code:
                raise ApiResponseError(response, status_code, str(e))
            else:
                raise ApiNotExistError(response)


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


class Client(object):
    def __init__(self, app, parser):
        self.app = app
        self.token = Token()
        self._parser = parser
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
        raise NotImplemented

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

        return self._parser.parse(response)

    def __getattr__(self, attr):
        return ClientWrapper(self, attr)


class OAuth2(object):
    def __init__(self, app, url, parser):
        self.app = app
        self.url = url
        self._session = requests.session()
        self._parser = parser

    def _parse_response(self, response):
        return self._parser.parse(response)

    def authorize(self, **kwargs):
        """  授权
        返回授权链接
        """
        raise NotImplemented

    def access_token(self, code, **kwargs):
        """ code换取access_token
        返回Token
        """
        raise NotImplemented