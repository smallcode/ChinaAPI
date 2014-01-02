# coding=utf-8
from requests import PreparedRequest


def parse_querystring(querystring):
    return dict([item.split('=') for item in querystring.split('&')])


def request_url(url, params):
    pre = PreparedRequest()
    pre.prepare_url(url, params)
    return pre.url