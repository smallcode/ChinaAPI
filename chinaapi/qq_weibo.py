# coding=utf-8
from .utils.clients import ApiClientBase, Method
from .utils.exceptions import ApiError


class ApiClient(ApiClientBase):
    #写入接口
    post_methods = ['add', 'del', 'create', 'delete', 'reply', 'comment', 'like', 'unlike', 'follow', 'addspecial',
                    'delspecial', 'addblacklist', 'delblacklist', 're_add', 'verify', 'createvote', 'vote']
    #含下划线的写入接口，如：t/add_pic
    _post_methods = ['add', 'del', 'upload']

    def __init__(self, app):
        super(ApiClient, self).__init__(app)
        self.openid = None
        self.clientip = None

    def set_openid(self, openid):
        self.openid = openid

    def set_clientip(self, clientip):
        self.clientip = clientip

    def prepare_url(self, segments, queries):
        queries['format'] = 'json'
        queries['oauth_consumer_key'] = self.app.key
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token
        if self.openid:
            queries['openid'] = self.openid
        if self.clientip:
            queries['clientip'] = self.clientip
        return 'https://graph.qq.com/{0:s}'.format('/'.join(segments))

    def prepare_method(self, method):
        method = method.lower()
        if method in self.post_methods or method.split('_')[0] in self._post_methods:
            return Method.POST
        return Method.GET

    def prepare_body(self, queries):
        files = None
        if 'pic' in queries:
            files = dict(pic=(queries.pop('pic')))
        return queries, files

    def parse_response(self, response):
        r = super(ApiClient, self).parse_response(response)
        if 'error_code' in r:
            raise ApiError(r.get('request', response.url), r.error_code, r.get('error', ''))
        return r

