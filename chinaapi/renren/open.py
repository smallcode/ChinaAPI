# coding=utf-8
from chinaapi.open import ClientBase, Method, OAuth2Base, Token, App
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
        r = response.json_dict()
        if 'error' in r and 'code' in r.error:
            raise ApiResponseError(response, r.error.code, r.error.get('message', ''))
        return r


class OAuth2(OAuth2Base):
    AUTH_URL = 'https://graph.renren.com/oauth/authorize'
    TOKEN_URL = 'https://graph.renren.com/oauth/token'

    def __init__(self, app):
        super(OAuth2, self).__init__(app)

    def _parse_token(self, response):
        r = response.json_dict()
        if 'error_code' in r:
            raise ApiResponseError(response, r.error_code, r.get('error_description', r.get('error', '')))
        return Token(**r)


