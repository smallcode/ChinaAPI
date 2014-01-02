# coding=utf-8
from chinaapi.exceptions import ApiResponseError
from chinaapi.open import OAuth2Base, Token as TokenBase, App


class Token(TokenBase):
    """
    douban_user_id：豆瓣用户ID
    """

    def __init__(self, access_token=None, expires_in=None, refresh_token=None, **kwargs):
        super(Token, self).__init__(access_token, expires_in, refresh_token, **kwargs)
        self.douban_user_id = kwargs.pop('douban_user_id', None)


class OAuth2(OAuth2Base):
    def __init__(self, app=App()):
        super(OAuth2, self).__init__(app, 'https://www.douban.com/service/auth2/')

    def _prepare_access_token_url(self):
        return self._url + 'token'

    def _prepare_authorize_url(self):
        return self._url + 'auth'

    def _parse_token(self, response):
        data = super(OAuth2, self)._parse_token(response)
        return Token(**data)

    def _parse_response(self, response):
        r = super(OAuth2, self)._parse_response(response)
        if 'code' in r and 'msg' in r:
            raise ApiResponseError(response, r.code, r.msg)
        return r