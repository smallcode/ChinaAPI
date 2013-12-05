# coding=utf-8
from .utils.clients import ApiClientBase, Method
from .utils.exceptions import ApiError


VALUE_TO_STR = {
    'friends': lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type(u'a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}


class ApiClient(ApiClientBase):
    #写接口
    post_methods = ['add', 'del', 'create', 'delete', 'update', 'verify']
    #含下划线的写入接口，如：t/add_pic
    _post_methods = ['add', 'del', 'upload', 'update']
    friends_post_methods = ['addspecial','delspecial', 'addblacklist', 'delblacklist']
    t_post_methods = ['re_add', 'reply', 'comment', 'like', 'unlike']
    fav_post_methods = ['addht', 'addt', 'delht', 'delt']
    vote_post_methods = ['createvote', 'vote']

    def __init__(self, app):
        super(ApiClient, self).__init__(app)
        self.openid = None
        self.clientip = None

    def set_openid(self, openid):
        self.openid = openid

    def set_clientip(self, clientip):
        self.clientip = clientip

    @staticmethod
    def get_api_url(segments):
        return 'https://open.t.qq.com/api/{0}'.format('/'.join(segments))

    def prepare_url(self, segments, queries):
        queries['oauth_version'] = '2.a'
        queries['format'] = 'json'
        queries['oauth_consumer_key'] = self.app.key
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token
        if self.openid:
            queries['openid'] = self.openid
        if 'clientip' not in queries and self.clientip:
            queries['clientip'] = self.clientip
        return self.get_api_url(segments)

    def prepare_method(self, segments):
        if len(segments) != 2:
            raise ApiError(self.get_api_url(segments), 404, 'Request Api not found!')
        model, method = tuple([segment.lower() for segment in segments])
        if method in self.post_methods or method.split('_')[0] in self._post_methods:
            return Method.POST
        elif model == 't' and method in self.t_post_methods:
            return Method.POST
        elif model == 'friends' and method in self.friends_post_methods:
            return Method.POST
        elif model == 'list' and method != 'timeline':  # 只有timeline接口是读接口，其他全是写接口
            return Method.POST
        elif model == 'fav' and method in self.fav_post_methods:
            return Method.POST
        elif model == 'lbs':  # 全是写接口
            return Method.POST
        elif model == 'vote' and method in self.vote_post_methods:
            return Method.POST
        return Method.GET

    def prepare_body(self, queries):
        files = None
        if 'pic' in queries:
            files = dict(pic=(queries.pop('pic')))
        return queries, files

    def parse_response(self, response):
        if response.status_code == 404 and not response.content:
            raise ApiError(self.get_error_request(response), response.status_code, 'Request Api not found!')
        r = super(ApiClient, self).parse_response(response)
        if 'ret' in r and r.ret != 0:
            error_code = '{0}-{1}'.format(r.ret, r.get('errcode', r.ret))
            raise ApiError(self.get_error_request(response), error_code, r.get('msg', ''))
        return r

