# coding=utf-8
from .utils.api import Client, Method, Response
from .utils.exceptions import ApiResponseError
from .utils import jsonDict
from datetime import datetime
import hmac


VALUE_TO_STR = {
    type(datetime.now()): lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type(u'a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}

DEFAULT_VALUE_TO_STR = lambda x: str(x)


class ApiResponse(Response):
    def __init__(self, requests_response):
        super(ApiResponse, self).__init__(requests_response)

    def _parse_response(self):
        try:
            return super(ApiResponse, self).get_data()
        except ApiResponseError:
            try:
                text = self.requests_response.text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                return jsonDict.loads(text)
            except ValueError, e:
                raise ApiResponseError(self.requests_response, 15, 'json decode error', 'ism.json-decode-error',
                                       "json-error: %s || %s" % (str(e), self.requests_response.text))

    def get_data(self):
        r = self._parse_response()
        keys = r.keys()
        if keys:
            key = keys[0]
            if 'error_response' in keys:
                error = r.error_response
                raise ApiResponseError(self.requests_response, error.get('code', ''), error.get('msg', ''),
                                       error.get('sub_code', ''), error.get('sub_msg', ''))
            return r[key]
        return r


class ApiClient(Client):
    def __init__(self, app):
        super(ApiClient, self).__init__(app, ApiResponse)

    def prepare_url(self, segments, queries):
        if segments[0] != 'taobao':
            segments.insert(0, 'taobao')
        queries['method'] = '.'.join(segments)
        return 'http://gw.api.taobao.com/router/rest'

    def prepare_method(self, segments):
        """
        淘宝接口全部使用POST提交
        """
        return Method.POST

    def sign(self, values):
        """
        Return encoded data and files
        """
        data, files = {}, {}
        args = {'app_key': self.app.key, 'sign_method': 'hmac', 'format': 'json', 'v': '2.0',
                'timestamp': datetime.now()}

        for k, v in values.items() + args.items():
            kk = k.replace('__', '.')
            if hasattr(v, 'read'):
                files[kk] = v
            elif v is not None:
                data[kk] = VALUE_TO_STR.get(type(v), DEFAULT_VALUE_TO_STR)(v)

        args_str = "".join(["%s%s" % (k, data[k]) for k in sorted(data.keys())])
        sign = hmac.new(self.app.secret)
        sign.update(args_str)
        data['sign'] = sign.hexdigest().upper()
        return data, files

    def prepare_body(self, queries):
        if not self.token.is_expires:
            queries['session'] = self.client.access_token
        return self.sign(queries)



