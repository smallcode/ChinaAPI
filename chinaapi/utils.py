# coding=utf-8
from urlparse import urlparse
from requests import PreparedRequest


def parse_querystring(querystring):
    if '?' in querystring:
        querystring = urlparse(querystring).query
    return dict([item.split('=', 1) for item in querystring.split('&')])


def request_url(url, params):
    pre = PreparedRequest()
    pre.prepare_url(url, params)
    return pre.url