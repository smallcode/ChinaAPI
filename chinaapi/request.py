# coding=utf-8
import types
import re

import requests

from .jsonDict import JsonDict, loads
from .exceptions import ApiResponseError


def json_dict(self):
    try:
        return self.json(object_hook=lambda pairs: JsonDict(pairs.iteritems()))
    except ValueError, e:
        try:
            self.raise_for_status()
        except requests.RequestException, e:
            raise ApiResponseError(self, message=u'%s, response: %s' % (e, self.text))
        else:
            raise ApiResponseError(self, e.__class__.__name__, u'%s, value: %s' % (e, self.text))


def jsonp_dict(self):
    return loads(re.search(r'(\{.*\})', self.text).group(1))


def add_method(response, *args, **kwargs):
    response.json_dict = types.MethodType(json_dict, response)
    response.jsonp_dict = types.MethodType(jsonp_dict, response)
    return response


class Request(object):
    def __init__(self):
        self._session = requests.session()
        self._session.hooks = dict(response=add_method)