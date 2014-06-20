# coding=utf-8
from chinaapi.exceptions import ApiResponseError
from chinaapi.open import *


class OAuth2(OAuth2Base):
    AUTH_URL = 'https://www.douban.com/service/auth2/auth'
    TOKEN_URL = 'https://www.douban.com/service/auth2/token'

    def _parse_token(self, response):
        r = response.json_dict()
        if 'code' in r and 'msg' in r:
            raise ApiResponseError(response, r.code, r.msg)
        return Token(**r)