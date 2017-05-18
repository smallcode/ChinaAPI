# coding=utf-8
import os
import random
import re
from chinaapi.web import ClientBase


class Client(ClientBase):
    @staticmethod
    def encrypt_password(e, m, s):
        def _encrypt_chunk(e, m, chunk):
            chunk = list(map(ord, chunk))

            # 补成偶数长度
            if not len(chunk) % 2 == 0:
                chunk.append(0)

            nums = [chunk[i] + (chunk[i + 1] << 8) for i in range(0, len(chunk), 2)]

            c = sum([n << i * 16 for i, n in enumerate(nums)])

            encrypted = pow(c, e, m)

            # 转成16进制并且去掉开头的0x
            return hex(encrypted)[2:]


        CHUNK_SIZE = 30  # 分段加密

        e, m = int(e, 16), int(m, 16)
        chunks = [s[:CHUNK_SIZE], s[CHUNK_SIZE:]] if len(s) > CHUNK_SIZE else [s]
        result = [_encrypt_chunk(e, m, chunk) for chunk in chunks]
        return ' '.join(result)[:-1]  # 去掉最后的'L'

    def get_encrypt_key(self):
        r = self._session.get('http://login.renren.com/ajax/getEncryptKey')
        return r.json()

    def get_show_captcha(self, email=None):
        r = self._session.post('http://www.renren.com/ajax/ShowCaptcha', data={'email': email})
        return r.json()

    def get_icode(self, fn):
        r = self._session.get("http://icode.renren.com/getcode.do?t=web_login&rnd=%s" % random.random())
        if r.status_code == 200 and r.raw.headers['content-type'] == 'image/jpeg':
            with open(fn, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
        else:
            raise Exception('get icode failure')

    def get_token(self, html=''):
        p = re.compile("get_check:'(.*)',get_check_x:'(.*)',env")

        if not html:
            r = self._session.get('http://www.renren.com')
            html = r.text

        result = p.search(html)
        return {
            'requestToken': result.group(1),
            '_rtk': result.group(2)
        }

    def login(self, username, password):
            key = self.get_encrypt_key()

            if self.get_show_captcha(username) == 1:
                fn = 'icode.%s.jpg' % os.getpid()
                self.get_icode(fn)
                print("Please input the code in file '%s':" % fn)
                icode = input().strip()
                os.remove(fn)
            else:
                icode = ''

            data = {
                'email': username,
                'origURL': 'http://www.renren.com/home',
                'icode': icode,
                'domain': 'renren.com',
                'key_id': 1,
                'captcha_type': 'web_login',
                'password': self.encrypt_password(key['e'], key['n'], password) if key['isEncrypt'] else password,
                'rkey': key.get('rkey', '')
            }
            url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
            r = self._session.post(url, data)
            result = r.json()
            if result['code']:
                self.email = username
                r = self._session.get(result['homeUrl'])
                return self.get_token(r.text)
            else:
                raise Exception('Login Error')