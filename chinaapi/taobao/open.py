# coding=utf-8
import base64
import hmac
from hashlib import md5
from datetime import datetime
from urllib import unquote
from chinaapi.open import ClientBase, OAuthBase, OAuth2Base, App, Token as TokenBase
from chinaapi.exceptions import ApiResponseError, ApiError
from chinaapi.utils import parse_querystring

DEFAULT_RETRIES = 3
DEFAULT_VALUE_TO_STR = lambda x: str(x)
VALUE_TO_STR = {
    type(datetime.now()): lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type(u'a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}
RETRY_SUB_CODES = {
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
}


def join_dict(data):
    return ''.join(["%s%s" % (k, v) for k, v in sorted(data.iteritems())])


class Client(ClientBase):
    def __init__(self, app=App(), retries=DEFAULT_RETRIES):
        super(Client, self).__init__(app, Token())
        self._retries = retries

    @property
    def session(self):
        return self.token.access_token

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
            queries['session'] = self.session
        queries.update({'app_key': self.app.key, 'sign_method': 'hmac', 'format': 'json', 'v': '2.0',
                        'timestamp': datetime.now()})

    def _prepare_body(self, queries):
        """
        Return encoded data and files
        """
        data, files = {}, {}
        for k, v in queries.items():
            kk = k.replace('__', '.')
            if hasattr(v, 'read'):
                files[kk] = v
            elif v is not None:
                data[kk] = VALUE_TO_STR.get(type(v), DEFAULT_VALUE_TO_STR)(v)
        data['sign'] = self._sign_by_hmac(data)
        return data, files

    def request(self, segments, **queries):
        url = self._prepare_url(segments, queries)
        self._prepare_queries(queries)
        data, files = self._prepare_body(queries)
        for count in xrange(self._retries, 0, -1):
            try:
                response = self._session.post(url, data=data, files=files)
                return self._parse_response(response)
            except ApiError, e:
                if e.sub_code in RETRY_SUB_CODES and count > 1:
                    for f in files.values():
                        f.seek(0)
                    continue
                raise e

    def _parse_response(self, response):
        r = response.json_dict()
        if 'error_response' in r:
            error = r.error_response
            raise ApiResponseError(response, error.get('code', ''), error.get('msg', ''),
                                   error.get('sub_code', ''), error.get('sub_msg', ''))
        else:
            keys = r.keys()
            if keys and keys[0].endswith('_response'):
                return r.get(keys[0])


def parse(response):
    r = response.json_dict()
    if 'error' in r:
        raise ApiResponseError(response, r.error, r.get('error_description', ''))
    return r


class Token(TokenBase):
    """
    taobao_user_nick：淘宝账号
    taobao_user_id：淘宝帐号对应id
    sub_taobao_user_nick：淘宝子账号
    sub_taobao_user_id：淘宝子账号对应id
    token_type：Access token的类型目前只支持bearer
    re_expires_in：Refresh token过期时间
    r1_expires_in：r1级别API或字段的访问过期时间
    r2_expires_in：r2级别API或字段的访问过期时间
    w1_expires_in：w1级别API或字段的访问过期时间
    w2_expires_in：w2级别API或字段的访问过期时间
    """

    def __init__(self, access_token=None, expires_in=None, refresh_token=None, **kwargs):
        super(Token, self).__init__(access_token, expires_in, refresh_token, **kwargs)
        self.taobao_user_nick = kwargs.pop('taobao_user_nick', None)
        self.taobao_user_id = kwargs.pop('taobao_user_id', None)
        self.sub_taobao_user_nick = kwargs.pop('sub_taobao_user_nick', None)
        self.sub_taobao_user_id = kwargs.pop('sub_taobao_user_id', None)
        self.token_type = kwargs.pop('token_type', None)
        self.re_expires_in = kwargs.pop('re_expires_in', None)
        self.r1_expires_in = kwargs.pop('r1_expires_in', None)
        self.r2_expires_in = kwargs.pop('r2_expires_in', None)
        self.w1_expires_in = kwargs.pop('w1_expires_in', None)
        self.w2_expires_in = kwargs.pop('w2_expires_in', None)


class OAuth2(OAuth2Base):
    def __init__(self, app):
        super(OAuth2, self).__init__(app, 'https://oauth.taobao.com/')

    def _parse_token(self, response):
        data = parse(response)
        return Token(**data)

    def _prepare_access_token_url(self):
        return self._url + 'token'

    def logoff(self, view='web'):
        """ 退出登录帐号，目前只支持web访问，起到的作用是清除taobao.com的cookie，并不是取消用户的授权。在WAP上访问无效。
        返回：用于退出登录的链接
        """
        return self._url + 'logoff?client_id={0}&view={1}'.format(self.app.key, view)


class OAuth(OAuthBase):
    """
    基于TOP协议的登录授权方式
    """

    def __init__(self, app):
        super(OAuth, self).__init__(app, 'http://container.open.taobao.com/container')

    def _sign_by_md5(self, data):
        message = join_dict(data) + self.app.secret
        return md5(message).hexdigest().upper()

    def authorize(self):
        return self._url + '?encode=utf-8&appkey={0}'.format(self.app.key)

    def refresh_token(self, refresh_token, top_session):
        params = dict(appkey=self.app.key, refresh_token=refresh_token, sessionkey=top_session)
        params['sign'] = self._sign_by_md5(params)
        response = self._session.get(self._url + '/refresh', params=params)
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
