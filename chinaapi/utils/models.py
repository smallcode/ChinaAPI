# coding=utf-8
import time


class Token(object):
    def __init__(self, access_token, expired_at=None, created_at=None, expires_in=None, refresh_token=None):
        """
        access_token：访问令牌
        expired_at：令牌到期日期，为timestamp格式
        created_at：令牌创建日期，为timestamp格式
        expires_in：令牌剩余授权时间的秒数
        refresh_token：用于刷新令牌
        """
        self.access_token = access_token
        self.expired_at = expired_at
        self.created_at = created_at
        self.expires_in = expires_in
        self.refresh_token = refresh_token

    @property
    def is_expires(self):
        return not self.access_token or (self.expired_at is not None and time.time() > self.expired_at)


class App(object):
    def __init__(self, key, secret=None, redirect_uri=None):
        self.key = key
        self.secret = secret
        self.redirect_uri = redirect_uri


class Account(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
