# coding=utf-8
from chinaapi.utils import jsonDict, models
import requests


class Method(object):
    GET = 'GET'
    POST = 'POST'


class ClientWrapper(object):
    def __init__(self, client, attr):
        """
        segments:用于保存路径片段
        """
        self._client = client
        self.segments = [attr]

    def __call__(self, **kwargs):
        return self._client.request(self.segments[-1], self.segments, **kwargs)

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            self.segments.append(attr)
        return self


class ApiClientBase(object):
    def __init__(self, app):
        self.app = app
        self.token = models.Token('')
        self.session = requests.session()

    def set_access_token(self, token):
        self.token = token

    def prepare_method(self, method):
        return method

    def prepare_url(self, segments, queries):
        raise NotImplemented

    def prepare_headers(self, headers, queries):
        return headers

    def prepare_body(self, queries):
        return queries, None

    def parse_response(self, response):
        return jsonDict.loads(response.text)

    def request(self, method, segments, **queries):
        method = self.prepare_method(method)
        url = self.prepare_url(segments, queries)
        headers = self.prepare_headers({'Accept-Encoding': 'gzip'}, queries)

        if method == Method.POST:
            data, files = self.prepare_body(queries)
            response = self.session.post(url, data=data, files=files, headers=headers)
        else:
            response = self.session.get(url, params=queries, headers=headers)

        return self.parse_response(response)

    def __getattr__(self, attr):
        return ClientWrapper(self, attr)