# coding=utf-8
import requests
from chinaapi.utils import jsonDict
from chinaapi.utils.models import Token
from chinaapi.utils.exceptions import ApiNotExistError, ApiResponseError


class Method(object):
    GET = 'GET'
    POST = 'POST'


class Response(object):
    def __init__(self, requests_response):
        self.requests_response = requests_response

    def get_data(self):
        try:
            return jsonDict.loads(self.requests_response.text)
        except ValueError, e:
            status_code = 200
            if self.requests_response.status_code == status_code:
                raise ApiResponseError(self.requests_response, status_code, str(e))
            else:
                raise ApiNotExistError(self.requests_response)


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
    def __init__(self, app, response_class):
        self.app = app
        self.token = Token()
        self.session = requests.session()
        self.response_class = response_class

    def set_token(self, token):
        self.token = token

    def prepare_method(self, segments):
        return segments

    def prepare_url(self, segments, queries):
        raise NotImplemented

    def prepare_headers(self, headers, queries):
        return headers

    def prepare_body(self, queries):
        return queries, None

    def request(self, segments, **queries):
        method = self.prepare_method(segments)
        url = self.prepare_url(segments, queries)
        headers = self.prepare_headers({'Accept-Encoding': 'gzip'}, queries)

        if method == Method.POST:
            data, files = self.prepare_body(queries)
            response = self.session.post(url, data=data, files=files, headers=headers)
        else:
            response = self.session.get(url, params=queries, headers=headers)

        return self.response_class(response).get_data()

    def __getattr__(self, attr):
        return ClientWrapper(self, attr)


class OAuth2(object):
    def __init__(self, app, url):
        self.app = app
        self.url = url
        self.session = requests.session()

    def authorize(self, **kwargs):
        raise NotImplemented

    def access_token(self, code, **kwargs):
        raise NotImplemented

    def revoke(self, access_token):
        raise NotImplemented