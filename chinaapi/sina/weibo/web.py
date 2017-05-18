# coding=utf-8
from chinaapi.utils import parse_querystring
from chinaapi.web import ClientBase
from chinaapi.exceptions import ApiResponseError
import urllib.request, urllib.parse, urllib.error
import re
import base64
import rsa
import binascii


class Client(ClientBase):
    JS_CLIENT = 'ssologin.js(v1.4.11)'
    LOGIN_URL = 'http://login.sina.com.cn/sso/login.php'
    PRE_LOGIN_URL = 'http://login.sina.com.cn/sso/prelogin.php'
    URL_REGEX = re.compile(r"replace\(['\"]+(.*)['\"]+\)")

    @staticmethod
    def encrypt_password(password, pre_data):
        public_key = int(pre_data.pubkey, 16)
        key = rsa.PublicKey(public_key, 65537)
        message = str(pre_data.servertime) + '\t' + str(pre_data.nonce) + '\n' + str(password)
        return binascii.b2a_hex(rsa.encrypt(message, key))

    def pre_login(self, su):
        params = {
            'client': self.JS_CLIENT,
            'entry': 'sso',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': su,
            'rsakt': 'mod',
            # '_': time.time(),
        }
        r = self._session.get(self.PRE_LOGIN_URL, params=params)
        return r.jsonp_dict()

    def login(self, username, password):
        su = base64.b64encode(urllib.parse.quote(username))
        pre_data = self.pre_login(su)
        sp = self.encrypt_password(password, pre_data)
        data = {
            'client': self.JS_CLIENT,
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '0',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': su,
            'service': 'miniblog',
            'servertime': pre_data.servertime,
            'nonce': pre_data.nonce,
            'pwencode': 'rsa2',
            'prelt': '164',
            'sp': sp,
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'rsakv': pre_data.rsakv,
        }
        response = self._session.post(self.LOGIN_URL, data=data)
        url = self.URL_REGEX.findall(response.text)[0]
        query = parse_querystring(url)
        if query['retcode'] != '0':
            raise ApiResponseError(response, query['retcode'], query['reason'])
        return self._session.get(url)

