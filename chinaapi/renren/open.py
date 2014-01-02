# coding=utf-8
from chinaapi.open import ClientBase, Method, OAuth2Base, Token as TokenBase, App
from chinaapi.exceptions import ApiResponseError


App = App


class Client(ClientBase):
    #写入接口
    _post_methods = ['put', 'share', 'remove', 'upload']

    def _prepare_url(self, segments, queries):
        return 'https://api.renren.com/v2/{0}'.format('/'.join(segments))

    def _prepare_method(self, segments):
        if segments[-1].lower() in self._post_methods:
            return Method.POST
        return Method.GET

    def _prepare_queries(self, queries):
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token

    def _parse_response(self, response):
        r = super(Client, self)._parse_response(response)
        if 'error' in r and 'code' in r.error:
            raise ApiResponseError(response, r.error.code, r.error.get('message', ''))
        return r


class Token(TokenBase):
    """
    token_type：Token类型，bearer或者mac
    scope：Access Token最终的访问范围，既用户实际授予的权限列表
    user：用户的个人信息，包含用户id，名称“name”，头像“avatar”（
          包含四种大小不同的尺寸“type”，大小依次为：“tiny”，“avatar”，“main”，“large”）
    mac_algorithm：当token_type参数为mac时返回该值
    mac_key：当token_type参数为mac时返回该值
    """

    class User(object):
        def __init__(self, id=None, name=None, avatar=None):
            self.id = id
            self.name = name
            self.avatar = avatar

    def __init__(self, access_token=None, expires_in=None, refresh_token=None, **kwargs):
        super(Token, self).__init__(access_token, expires_in, refresh_token, **kwargs)
        self.token_type = kwargs.pop('token_type', None)
        self.scope = kwargs.pop('scope', None)
        self.user = kwargs.pop('user', None)
        self.mac_algorithm = kwargs.pop('mac_algorithm', None)
        self.mac_key = kwargs.pop('mac_key', None)


class OAuth2(OAuth2Base):
    def __init__(self, app):
        super(OAuth2, self).__init__(app, 'https://graph.renren.com/oauth/')

    def _prepare_access_token_url(self):
        return self._url + 'token'

    def _parse_token(self, response):
        data = super(OAuth2, self)._parse_token(response)
        data['user'] = Token.User(**data.pop('user'))
        return Token(**data)

    def _parse_response(self, response):
        r = super(OAuth2, self)._parse_response(response)
        if 'error_code' in r:
            raise ApiResponseError(response, r.error_code, r.get('error_description', r.get('error', '')))
        return r


