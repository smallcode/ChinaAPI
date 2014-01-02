# coding=utf-8
from .request import Request


class ClientBase(Request):
    def __init__(self):
        super(ClientBase, self).__init__()
        self._session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'