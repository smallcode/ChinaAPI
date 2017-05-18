# coding=utf-8
from urllib.parse import urlparse
from requests import PreparedRequest


def parse_querystring(string):
    if '?' in string:
        string = urlparse(string).query
    return dict([item.split('=', 1) for item in string.split('&')])


def request_url(url, params):
    pre = PreparedRequest()
    pre.prepare_url(url, params)
    return pre.url