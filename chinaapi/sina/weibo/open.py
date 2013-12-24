# coding=utf-8
import base64
import hashlib
import hmac
from urlparse import urlparse
from chinaapi.utils.api import Response
from chinaapi.utils.open import ClientBase, Method, OAuth2Base, Token as TokenBase, App
from chinaapi.utils.exceptions import ApiResponseError
from chinaapi.utils import jsonDict


class ApiResponse(Response):
    def json(self):
        r = super(ApiResponse, self).json()
        if 'error_code' in r:
            raise ApiResponseError(self.response, r.error_code, r.get('error', ''))
        return r


class Client(ClientBase):
    #写入接口
    _post_methods = ['create', 'add', 'destroy', 'update', 'upload', 'repost', 'reply', 'send', 'post', 'invite',
                     'shield', 'order']
    #含下划线的写入接口，如：statuses/upload_url_text
    _underlined_post_methods = ['add', 'upload', 'destroy', 'update', 'set', 'cancel', 'not']

    def __init__(self, app=App()):
        super(Client, self).__init__(app, Token())

    def _prepare_url(self, segments, queries):
        if 'pic' in queries:
            prefix = 'upload.'
        elif 'remind' == segments[0]:
            prefix = 'rm.'
        else:
            prefix = ''
        return 'https://{0}api.weibo.com/2/{1}.json'.format(prefix, '/'.join(segments))

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
        if self.token.is_expires:
            queries['source'] = self.app.key  # 对于不需要授权的API操作需追加source参数
        else:
            self._session.headers['Authorization'] = 'OAuth2 %s' % self.token.access_token

    def _prepare_body(self, queries):
        files = self._isolated_files(queries, ['pic', 'image'])
        return queries, files

    def _parse_response(self, response):
        return ApiResponse(response).json()


class Token(TokenBase):
    """
    uid：授权用户的uid
    created_at：令牌创建日期，为timestamp格式
    """

    def __init__(self, access_token=None, expires_in=None, refresh_token=None, **kwargs):
        super(Token, self).__init__(access_token, expires_in, refresh_token, **kwargs)
        self.uid = kwargs.pop('uid', None)
        self.created_at = kwargs.pop('created_at', None)


class OAuth2(OAuth2Base):
    def __init__(self, app):
        super(OAuth2, self).__init__(app, 'https://api.weibo.com/oauth2/')

    def _parse_response(self, response):
        return ApiResponse(response).json()

    def _parse_token(self, response):
        data = super(OAuth2, self)._parse_token(response)
        data['created_at'] = data.pop('create_at', None)
        if 'expires_in' not in data:
            data['expires_in'] = data.pop('expire_in', None)
        return Token(**data)

    def revoke(self, access_token):
        """ 取消授权
        返回是否成功取消
        """
        response = self._session.get(self._url + 'revokeoauth2', params={'access_token': access_token})
        return self._parse_response(response).result

    def get_token_info(self, access_token):
        """ 获取access_token详细信息
        返回Token
        """
        response = self._session.post(self._url + 'get_token_info', data={'access_token': access_token})
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
        data = jsonDict.loads(base64decode(encoded_data))
        token = Token()
        token.access_token = data.oauth_token
        token.created_at = data.issued_at
        token.uid = data.user_id
        token.expires_in = data.expires
        is_valid = data.algorithm == u'HMAC-SHA256' and hmac.new(self.app.key, encoded_data,
                                                                 hashlib.sha256).digest() == sign
        return token, is_valid

    def login(self, username, password, allow_redirects=True):
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

        url = self._prepare_authorize_url()
        r = self._session.post(url, data=data, headers=headers, allow_redirects=allow_redirects)
        if allow_redirects:
            code_url = r.url
        else:
            code_url = r.headers['location']
        code = self._parse_querystring((urlparse(code_url)).query)['code']
        return self.access_token(code=code)