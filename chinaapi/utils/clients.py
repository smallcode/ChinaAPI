# coding=utf-8
from chinaapi.utils import jsonDict, models
import requests
from chinaapi.utils.exceptions import ApiNotExistError, ApiResponseError


class Method(object):
    GET = 'GET'
    POST = 'POST'


class ClientWrapper(object):
    def __init__(self, client, attr):
        """
        segments:用于保存路径片段
        """
        self._client = client
        self._segments = [attr]

    def __call__(self, **kwargs):
        return self._client.request(self._segments, **kwargs)

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            self._segments.append(attr)
        return self


class ApiClientBase(object):
    def __init__(self, app):
        self.app = app
        self.token = models.Token('')
        self.session = requests.session()

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

    def parse_response(self, response):
        try:
            return jsonDict.loads(response.text)
        except ValueError, e:
            status_code = 200
            if response.status_code == status_code:
                raise ApiResponseError(response, status_code, str(e))
            else:
                raise ApiNotExistError(response)

    def request(self, segments, **queries):
        method = self.prepare_method(segments)
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
