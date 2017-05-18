# coding=utf-8
import base64
import hashlib
import hmac
from chinaapi.utils import parse_querystring
from chinaapi.open import ClientBase, Method, OAuth2Base, Token, App
from chinaapi.exceptions import ApiResponseError
from chinaapi.jsonDict import loads

App = App

RETRY_CODES = {
    10001: 'system error',
    10011: 'RPC error',
    20205: 'in block',
    21405: "couldn't connect to host | Operation timed out after 2000 milliseconds",
    23201: 'Backend Service Connect Timeout',
}


def parse(response):
    r = response.json_dict()
    if 'error_code' in r:
        raise ApiResponseError(response, r.error_code, r.get('error', ''))
    return r


class Client(ClientBase):
    #写入接口
    _post_methods = ['create', 'add', 'destroy', 'update', 'upload', 'repost', 'reply', 'send', 'post', 'invite',
                     'shield', 'order']
    #含下划线的写入接口，如：statuses/upload_url_text
    _underlined_post_methods = ['add', 'upload', 'destroy', 'update', 'set', 'cancel', 'not']

    def _parse_response(self, response):
        return parse(response)

    def _prepare_url(self, segments, queries):
        if 'pic' in queries:
            prefix = 'upload.'
        elif 'remind' == segments[0]:
            prefix = 'rm.'
        else:
            prefix = ''
        url = 'https://{0}api.weibo.com/2/{1}.json'.format(prefix, '/'.join(segments))
        if 'like' in segments:
            # like操作需source和access_token参数，否则无法执行
            queries['source'] = self.app.key
            if not self.token.is_expires:
                queries['access_token'] = self.token.access_token
            return url.replace('weibo.com', 'weibo.cn')
        return url

    def _prepare_method(self, segments):
        segment = segments[-1].lower()
        if segment in self._post_methods:
            return Method.POST
        elif '_' in segment:
            splits = segment.split('_')
            if splits[0] in self._underlined_post_methods or splits[-1] == 'update':
                return Method.POST
        return Method.GET

    def _prepare_queries(self, queries):
        if self.token.access_token is None:
            queries['source'] = self.app.key  # 对于不需要授权的API操作需追加source参数
        if not self.token.is_expires:
            self._session.headers['Authorization'] = 'OAuth2 %s' % self.token.access_token

    def _is_retry_error(self, e):
        return e.code in RETRY_CODES


class OAuth2(OAuth2Base):
    BASE_URL = 'https://api.weibo.com/oauth2/'
    AUTH_URL = BASE_URL + 'authorize'
    TOKEN_URL = BASE_URL + 'access_token'

    def _parse_token(self, response):
        data = parse(response)
        data['created_at'] = data.get('create_at', None)
        if 'expires_in' not in data:
            data['expires_in'] = data.get('expire_in', None)
        return Token(**data)

    def revoke(self, access_token):
        """ 取消授权
        返回是否成功取消
        """
        response = self._session.get(self.BASE_URL + 'revokeoauth2', params={'access_token': access_token})
        return parse(response).result

    def get_token_info(self, access_token):
        """ 获取access_token详细信息
        返回Token
        """
        response = self._session.post(self.BASE_URL + 'get_token_info', data={'access_token': access_token})
        token = self._parse_token(response)
        token.access_token = access_token
        return token

    def parse_signed_request(self, signed_request):
        """  用于站内应用
        signed_request: 应用框架在加载时会通过向Canvas URL post的参数signed_request
        Returns: Token, is_valid (令牌, 是否有效)
        """

        def base64decode(s):
            appendix = '=' * (4 - len(s) % 4)
            return base64.b64decode(s.replace('-', '+').replace('_', '/') + appendix)

        encoded_sign, encoded_data = signed_request.split('.', 1)
        sign = base64decode(encoded_sign)
        data = loads(base64decode(encoded_data))
        token = Token(data.oauth_token, data.expires, uid=data.user_id, created_at=data.issued_at, **data)
        is_valid = data.algorithm == 'HMAC-SHA256' and hmac.new(self.app.key, encoded_data,
                                                                 hashlib.sha256).digest() == sign
        return token, is_valid

    def get_code(self, username, password, allow_redirects=True):
        data = {"client_id": self.app.key,
                "redirect_uri": self.app.redirect_uri,
                "userId": username,
                "passwd": password,
                "isLoginSina": "0",
                "action": "submit",
                "response_type": "code",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Host": "api.weibo.com",
            "Referer": self.authorize()
        }

        r = self._session.post(self.AUTH_URL, data=data, headers=headers, allow_redirects=allow_redirects)
        if allow_redirects:
            code_url = r.url
        else:
            code_url = r.headers['location']
        query = parse_querystring(code_url)
        return query['code']
