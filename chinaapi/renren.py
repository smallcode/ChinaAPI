# coding=utf-8
from .utils.clients import ApiClientBase, Method
from .utils.exceptions import ApiError


class ApiClient(ApiClientBase):
    #写入接口
    post_methods = ['put', 'share', 'remove', 'upload']

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

    def parse_response(self, response):
        r = super(ApiClient, self).parse_response(response)
        if 'error' in r:
            raise ApiError(self.get_error_request(response), r.error.get('code', ''), r.error.get('message', ''))
        return r

