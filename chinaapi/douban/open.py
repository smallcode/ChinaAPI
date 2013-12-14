# coding=utf-8
from chinaapi.utils.exceptions import ApiResponseError
from chinaapi.utils.open import OAuth2Base, Token


class OAuth2(OAuth2Base):
    def __init__(self, app):
        super(OAuth2, self).__init__(app, 'https://www.douban.com/service/auth2/')

    def _get_access_token_url(self):
        return self._url + 'token'

    def _get_authorize_url(self):
        return self._url + 'auth'

    def _parse_token(self, response):
        data = super(OAuth2, self)._parse_token(response)
        access_token = data.get('access_token', None)
        uid = data.get('douban_user_id', None)
        refresh_token = data.get('refresh_token', None)
        expires_in = data.get('expires_in', None)

        token = Token(access_token, refresh_token=refresh_token, uid=uid)
        token.expires_in = expires_in
        return token

    def _parse_response(self, response):
        r = super(OAuth2, self)._parse_response(response)
        if 'code' in r and 'msg' in r:
            raise ApiResponseError(response, r.code, r.msg)
        return r