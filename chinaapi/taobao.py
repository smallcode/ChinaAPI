# coding=utf-8
from .utils.clients import ApiClientBase, Method
from .utils.exceptions import ApiError
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


class ApiClient(ApiClientBase):
    def prepare_url(self, segments, queries):
        if segments[0] != 'taobao':
            segments.insert(0, 'taobao')
        queries['method'] = '.'.join(segments)
        return 'http://gw.api.taobao.com/router/rest'

    def prepare_method(self, method):
        return Method.POST

    def sign(self, values):
        """Return encoded data and files
        """
        data, files = {}, {}
        if not values:
            raise NotImplementedError('no values')
        args = {'app_key': self.app.key, 'sign_method': 'hmac', 'format': 'json', 'v': '2.0', 'timestamp': datetime.now()}

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

    def pre_parse_response(self, response):
        try:
            return super(ApiClient, self).parse_response(response)
        except ValueError:
            try:
                text = response.text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                return jsonDict.loads(text)
            except ValueError, e:
                return {
                    "error_response": {"msg": "json decode error", "sub_code": "ism.json-decode-error",
                                       "code": 15, "sub_msg": "json-error: %s || %s" % (str(e), response.text)}}

    def parse_response(self, response):
        r = self.pre_parse_response(response)
        if 'error_response' in r:
            raise ApiError(response.url, **r['error_response'])
        return r


