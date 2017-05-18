# coding=utf-8
from chinaapi.web import ClientBase
from chinaapi.exceptions import ApiResponseError
from hashlib import md5
import time

ERROR = {
    'error3': '用户名或密码错误',
}


class Client(ClientBase):
    def login(self, username, password):
        password = md5(password).hexdigest().lower()
        data = dict(userid=username,
                    password=password,
                    appid=9999,
                    persistentcookie=1,
                    s=time.time(),
                    b=7,
                    w=1440,
                    pwdtype=1,
                    v=26,
        )
        r = self._session.post('https://passport.sohu.com/sso/login.jsp', data=data)
        if 'success' not in r.content:
            raise ApiResponseError(r, 0, r.content.replace('\n', ''))
        return r

