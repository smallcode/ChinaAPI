# coding=utf-8
from .utils.api import Client, Method, Parser
from .utils.exceptions import ApiResponseError


class ApiParser(Parser):
    def parse(self, response):
        r = super(ApiParser, self).parse(response)
        if 'error' in r:
            raise ApiResponseError(response, r.error.get('code', ''), r.error.get('message', ''))
        return r


class ApiClient(Client):
    #写入接口
    _post_methods = ['put', 'share', 'remove', 'upload']

    def __init__(self, app):
        super(ApiClient, self).__init__(app, ApiParser)

    def _prepare_url(self, segments, queries):
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token
        return 'https://api.renren.com/v2/{0}'.format('/'.join(segments))

    def _prepare_method(self, segments):
        if segments[-1].lower() in self._post_methods:
            return Method.POST
        return Method.GET

    def _prepare_body(self, queries):
        files = self._isolated_files(queries, ['file'])
        return queries, files


