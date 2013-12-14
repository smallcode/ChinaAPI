# coding=utf-8
from .utils.exceptions import ApiResponseError
from .utils.open import OAuth2Base, ParserBase, Token


class ApiParser(ParserBase):
    def parse_response(self, response):
        r = super(ApiParser, self).parse_response(response)
        if 'code' in r and 'msg' in r:
            raise ApiResponseError(response, r.code, r.msg)
        return r


class ApiOAuth2(OAuth2Base, ApiParser):
    def __init__(self, app):
        super(ApiOAuth2, self).__init__(app, 'https://www.douban.com/service/auth2/')

    def _get_access_token_url(self):
        return self._url + 'token'

    def _get_authorize_url(self):
        return self._url + 'auth'

    def _parse_token(self, response):
        data = super(ApiOAuth2, self)._parse_token(response)
        access_token = data.get('access_token', None)
        uid = data.get('douban_user_id', None)
        refresh_token = data.get('refresh_token', None)
        expires_in = data.get('expires_in', None)

        token = Token(access_token, refresh_token=refresh_token, uid=uid)
        token.expires_in = expires_in
        return token