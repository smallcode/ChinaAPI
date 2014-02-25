# coding=utf-8
from chinaapi.exceptions import ApiResponseError
from chinaapi.open import OAuth2Base, Token, App


class OAuth2(OAuth2Base):
    AUTH_URL = 'https://www.douban.com/service/auth2/auth'
    TOKEN_URL = 'https://www.douban.com/service/auth2/token'

    def __init__(self, app=App()):
        super(OAuth2, self).__init__(app)

    def _parse_token(self, response):
        r = response.json_dict()
        if 'code' in r and 'msg' in r:
            raise ApiResponseError(response, r.code, r.msg)
        return Token(**r)