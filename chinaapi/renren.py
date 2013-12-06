# coding=utf-8
from .utils.api import Client, Method, Response
from .utils.exceptions import ApiResponseError


class ApiResponse(Response):
    def __init__(self, requests_response):
        super(ApiResponse, self).__init__(requests_response)

    def get_data(self):
        r = super(ApiResponse, self).get_data()
        if 'error' in r:
            raise ApiResponseError(self.requests_response, r.error.get('code', ''), r.error.get('message', ''))
        return r


class ApiClient(Client):
    #写入接口
    post_methods = ['put', 'share', 'remove', 'upload']

    def __init__(self, app):
        super(ApiClient, self).__init__(app, ApiResponse)

    def prepare_url(self, segments, queries):
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token
        return 'https://api.renren.com/v2/{0}'.format('/'.join(segments))

    def prepare_method(self, segments):
        segment = segments[-1].lower()
        if segment in self.post_methods:
            return Method.POST
        return Method.GET

    def prepare_body(self, queries):
        files = None
        if 'file' in queries:
            files = dict(file=(queries.pop('file')))
        return queries, files
