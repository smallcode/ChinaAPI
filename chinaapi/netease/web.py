# coding=utf-8
from chinaapi.exceptions import ApiResponseError
from chinaapi.web import ClientBase
from requests.utils import dict_from_cookiejar


class Client(ClientBase):
    def login(self, username, password):
        data = dict(
            username=username,
            password=password,
            type=1,
            product=163,
            savelogin=1,
            url='http://www.163.com/special/0077450P/login_frame.html',
            url2='http://www.163.com/special/0077450P/login_frame.html',
            noRedirect=1,
        )
        r = self._session.post('https://reg.163.com/logins.jsp', data=data)
        cookies = dict_from_cookiejar(r.cookies)
        if 'NTES_PASSPORT' not in cookies:
            raise ApiResponseError(r, 0, r.text)
        return r

