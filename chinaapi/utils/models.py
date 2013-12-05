# coding=utf-8
import time


class Token(object):
    def __init__(self, access_token, expired_at=None, created_at=None):
        self.access_token = access_token
        self.expired_at = expired_at  # expired_at表示到期日期，为timestamp格式
        self.created_at = created_at

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
