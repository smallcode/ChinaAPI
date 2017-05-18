# coding=utf-8
import base64
import hmac
from hashlib import md5
from datetime import datetime
from urllib.parse import unquote
from chinaapi.open import ClientBase, OAuthBase, OAuth2Base, App, Token
from chinaapi.exceptions import ApiResponseError
from chinaapi.utils import parse_querystring

DEFAULT_VALUE_TO_STR = lambda x: str(x)
VALUE_TO_STR = {
    type(datetime.now()): lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type('a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}
RETRY_SUB_CODES = (
    'isp.top-remote-connection-timeout',
    'isp.top-remote-connection-timeout-tmall',
    'isp.top-remote-service-unavailable',
    'isp.top-remote-service-unavailable-tmall',
    'isp.top-remote-unknown-error',
    'isp.top-remote-unknown-error-tmall',
    'isp.remote-connection-error',
    'isp.remote-connection-error-tmall',
    'isp.item-update-service-error:GENERIC_FAILURE',
    'isp.item-update-service-error:IC_SYSTEM_NOT_READY_TRY_AGAIN_LATER',
    'ism.json-decode-error',
    'ism.demo-error',
)


def join_dict(data):
    return ''.join(["%s%s" % (k, v) for k, v in sorted(data.items())])


class Client(ClientBase):
    def __init__(self, app=App(), session=None):
        super(Client, self).__init__(app, Token(session))

    def _get_session(self):
        return self.token.access_token

    def _set_session(self, session):
        self.token.access_token = session

    session = property(_get_session, _set_session)

    def _sign_by_hmac(self, data):
        message = join_dict(data)
        h = hmac.new(self.app.secret)
        h.update(message)
        return h.hexdigest().upper()

    def _prepare_url(self, segments, queries):
        if segments[0] != 'taobao':
            segments.insert(0, 'taobao')
        queries['method'] = '.'.join(segments)
        return 'http://gw.api.taobao.com/router/rest'

    def _prepare_queries(self, queries):
        if not self.token.is_expires:
            queries['session'] = self.token.access_token
        queries.update({'app_key': self.app.key, 'sign_method': 'hmac', 'format': 'json', 'v': '2.0',
                        'timestamp': datetime.now()})

    def _prepare_body(self, queries):
        """
        Return encoded data and files
        """
        data, files = {}, {}
        for k, v in list(queries.items()):
            kk = k.replace('__', '.')
            if hasattr(v, 'read'):
                files[kk] = v
            elif v is not None:
                data[kk] = VALUE_TO_STR.get(type(v), DEFAULT_VALUE_TO_STR)(v)
        data['sign'] = self._sign_by_hmac(data)
        return data, files

    def _parse_response(self, response):
        r = response.json_dict()
        if 'error_response' in r:
            error = r.error_response
            raise ApiResponseError(response, error.get('code', ''), error.get('msg', ''),
                                   error.get('sub_code', ''), error.get('sub_msg', ''))
        else:
            keys = list(r.keys())
            if keys and keys[0].endswith('_response'):
                return r.get(keys[0])

    def _is_retry_error(self, e):
        return e.sub_code in RETRY_SUB_CODES


def parse(response):
    r = response.json_dict()
    if 'error' in r:
        raise ApiResponseError(response, r.error, r.get('error_description', ''))
    return r


class OAuth2(OAuth2Base):
    AUTH_URL = 'https://oauth.taobao.com/authorize'
    TOKEN_URL = 'https://oauth.taobao.com/token'

    def _parse_token(self, response):
        data = parse(response)
        return Token(**data)

    def logoff(self, view='web'):
        """ 退出登录帐号，目前只支持web访问，起到的作用是清除taobao.com的cookie，并不是取消用户的授权。在WAP上访问无效。
        返回：用于退出登录的链接
        """
        return 'https://oauth.taobao.com/logoff?client_id={0}&view={1}'.format(self.app.key, view)


class OAuth(OAuthBase):
    """
    基于TOP协议的登录授权方式
    """
    URL = 'http://container.open.taobao.com/container'

    def _sign_by_md5(self, data):
        message = join_dict(data) + self.app.secret
        return md5(message).hexdigest().upper()

    def authorize(self):
        return self.URL + '?encode=utf-8&appkey={0}'.format(self.app.key)

    def refresh_token(self, refresh_token, top_session):
        params = dict(appkey=self.app.key, refresh_token=refresh_token, sessionkey=top_session)
        params['sign'] = self._sign_by_md5(params)
        response = self._session.get(self.URL + '/refresh', params=params)
        return parse(response)

    def validate_sign(self, top_parameters, top_sign, top_session):
        """  验证签名是否正确（用于淘宝帐号授权）（已测试成功，不要更改）
        """
        top_sign = unquote(top_sign)
        top_parameters = unquote(top_parameters)
        sign = base64.b64encode(md5(self.app.key + top_parameters + top_session + self.app.secret).digest())
        return top_sign == sign

    @staticmethod
    def decode_parameters(top_parameters):
        """  将top_parameters字符串解码并转换为字典，（已测试成功，不要更改）
        """
        parameters = base64.decodestring(unquote(top_parameters))
        return parse_querystring(parameters)
