# coding=utf-8
from chinaapi.open import ClientBase, Method, OAuth2Base, Token, App
from chinaapi.exceptions import ApiResponseError
from chinaapi.utils import parse_querystring


IS_POST_METHOD = {
    'user': lambda m: m in ['verify'],
    'friends': lambda m: m in ['addspecial', 'delspecial', 'addblacklist', 'delblacklist'],
    't': lambda m: m in ['re_add', 'reply', 'comment', 'like', 'unlike'],
    'fav': lambda m: m in ['addht', 'addt', 'delht', 'delt'],
    'vote': lambda m: m in ['createvote', 'vote'],
    'list': lambda m: m != 'timeline',  # 只有timeline接口是读接口，其他全是写接口
    'lbs': lambda m: True  # 全是写接口
}

DEFAULT_IS_POST_METHOD = lambda m: False

RET = {
    0: '成功返回',
    1: '参数错误',
    2: '频率受限',
    3: '鉴权失败',
    4: '服务器内部错误',
    5: '用户错误',
    6: '未注册微博',
    7: '未实名认证'
}


def parse(response):
    r = response.json_dict()
    if 'ret' in r and r.ret != 0:
        raise ApiResponseError(response, r.ret, RET.get(r.ret, ''), r.get('errcode', ''), r.get('msg', ''))
    if 'data' in r:
        return r.data
    return r


class Client(ClientBase):
    # 写接口
    _post_methods = ['add', 'del', 'create', 'delete', 'update', 'upload']

    def __init__(self, app=App(), token=Token(), openid=None, clientip=None):
        super(Client, self).__init__(app, token)
        self.openid = openid
        self.clientip = clientip

    def _parse_response(self, response):
        return parse(response)

    def _prepare_url(self, segments, queries):
        """
        因del为Python保留字，无法作为方法名，需将del替换为delete，并在此处进行反向转换。
        """
        if len(segments) == 2 and segments[0] != 'list' and segments[1] == 'delete':  # list本身有delete方法，需排除
            segments[1] = segments[1].replace('delete', 'del')
        return 'https://open.t.qq.com/api/{0}'.format('/'.join(segments))

    def _prepare_method(self, segments):
        model, method = tuple([segment.lower() for segment in segments])
        if method.split('_')[0] in self._post_methods:
            return Method.POST
        elif IS_POST_METHOD.get(model, DEFAULT_IS_POST_METHOD)(method):
            return Method.POST
        return Method.GET

    def _prepare_queries(self, queries):
        queries.update(oauth_version='2.a', format='json', oauth_consumer_key=self.app.key)
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token
        if self.openid:
            queries['openid'] = self.openid
        if 'clientip' not in queries and self.clientip:
            queries['clientip'] = self.clientip


class OAuth2(OAuth2Base):
    AUTH_URL = 'https://open.t.qq.com/cgi-bin/oauth2/authorize'
    TOKEN_URL = 'https://open.t.qq.com/cgi-bin/oauth2/access_token'

    def _parse_token(self, response):
        data = parse_querystring(response.text)
        if 'errorCode' in data:
            raise ApiResponseError(response, data['errorCode'], data.get('errorMsg', '').strip("'"))
        return Token(**data)

    def revoke(self, **kwargs):
        """ 取消授权
        请求参数：oauth或openid&openkey标准参数
        返回是否成功取消
        """
        kwargs['format'] = 'json'
        response = self._session.get('http://open.t.qq.com/api/auth/revoke_auth', params=kwargs)
        parse(response)
        return True  # 没有异常说明ret=0（ret: 0-成功，非0-失败）
