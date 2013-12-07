# coding=utf-8
from .utils.api import Client, Parser
from .utils.exceptions import ApiResponseError, ApiError
from datetime import datetime
import hmac


VALUE_TO_STR = {
    type(datetime.now()): lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type(u'a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}

DEFAULT_VALUE_TO_STR = lambda x: str(x)

RETRY_SUB_CODES = {'isp.top-remote-unknown-error', 'isp.top-remote-connection-timeout',
                   'isp.remote-connection-error', 'mz.emptybody',
                   'isp.top-remote-service-unavailable', 'isp.top-remote-connection-timeout-tmall',
                   'isp.item-update-service-error:GENERIC_FAILURE',
                   'isp.item-update-service-error:IC_SYSTEM_NOT_READY_TRY_AGAIN_LATER',
                   'ism.json-decode-error', 'ism.demo-error'}


class ApiParser(Parser):
    # def pre_parse_response(self, response):
    #     try:
    #         return super(ApiParser, self).parse(response)
    #     except ApiResponseError:
    #         try:
    #             text = response.text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
    #             return jsonDict.loads(text)
    #         except ValueError, e:
    #             raise ApiResponseError(response, 15, 'json decode error', 'ism.json-decode-error',
    #                                    "json-error: %s || %s" % (str(e), response.text))

    def parse(self, response):
        r = super(ApiParser, self).parse(response)
        keys = r.keys()
        if keys:
            key = keys[0]
            if 'error_response' in keys:
                error = r.error_response
                raise ApiResponseError(response, error.get('code', ''), error.get('msg', ''),
                                       error.get('sub_code', ''), error.get('sub_msg', ''))
            return r[key]


class ApiClient(Client):
    def __init__(self, app, retry_count=3):
        super(ApiClient, self).__init__(app, ApiParser())
        self._retry_count = retry_count

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

    @staticmethod
    def _hashing(message, secret):
        sign = hmac.new(secret)
        sign.update(message)
        return sign.hexdigest().upper()

    def _sign(self, data):
        message = "".join(["%s%s" % (k, data[k]) for k in sorted(data.keys())])
        return self._hashing(message, self.app.secret)

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
        data['sign'] = self._sign(data)
        return data, files

    def request(self, segments, **queries):
        url = self._prepare_url(segments, queries)
        self._prepare_queries(queries)
        data, files = self._prepare_body(queries)
        for count in xrange(self._retry_count, 0, -1):
            try:
                response = self._session.post(url, data=data, files=files)
                return self._parser.parse(response)
            except ApiError, e:
                if e.sub_message in RETRY_SUB_CODES and count > 1:
                    for f in files.values():
                        f.seek(0)
                    continue
                raise e

