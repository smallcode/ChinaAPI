# coding=utf-8


class ApiClient(object):
    def __init__(self, app):
        self.app = app
        self.token = None

    def set_access_token(self, token):
        self.token = token


class WebClient(object):
    pass


class WapClient(object):
    pass