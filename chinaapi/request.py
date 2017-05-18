# coding=utf-8
import types
import re

import requests

from .jsonDict import JsonDict, loads
from .exceptions import ApiResponseError


def json_dict(self):
    try:
        return self.json(object_hook=lambda pairs: JsonDict(iter(pairs.items())))
    except ValueError as e:
        try:
            self.raise_for_status()
        except requests.RequestException as e:
            raise ApiResponseError(self, message='%s, response: %s' % (e, self.text))
        else:
            raise ApiResponseError(self, e.__class__.__name__, '%s, value: %s' % (e, self.text))


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