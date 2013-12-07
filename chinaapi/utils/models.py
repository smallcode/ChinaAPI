# coding=utf-8
import time


class Token(object):
    def __init__(self, access_token=None, expired_at=None, created_at=None, refresh_token=None, uid=None):
        """
        access_token：访问令牌
        expired_at：令牌到期日期，为timestamp格式
        created_at：令牌创建日期，为timestamp格式
        expires_in：令牌剩余授权时间的秒数
        refresh_token：用于刷新令牌
        uid：授权用户的uid
        """
        self.access_token = access_token
        self.expired_at = expired_at
        self.created_at = created_at
        self.refresh_token = refresh_token
        self.uid = uid

    def set_expires_in(self, expires_in):
        if expires_in:
            current = int(time.time())
            self.expired_at = expires_in + current

    @property
    def is_expires(self):
        return not self.access_token or (self.expired_at is not None and time.time() > self.expired_at)


class App(object):
    def __init__(self, key, secret, redirect_uri=''):
        self.key = key
        self.secret = secret
        self.redirect_uri = redirect_uri


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
