# coding=utf-8


class ApiClient(object):
    def __init__(self, app):
        self.app = app
        self.access_token = None

    def set_access_token(self, access_token):
        self.access_token = access_token


class WebClient(object):
    pass


class WapClient(object):
    pass