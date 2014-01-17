# coding=utf-8
import types
import requests
import re
from .jsonDict import JsonDict, loads
from .exceptions import ApiResponseValueError, NotExistApi


def json_dict(self):
    try:
        return self.json(object_hook=lambda pairs: JsonDict(pairs.iteritems()))
    except ValueError, e:
        if self.status_code == 200:
            raise ApiResponseValueError(self, e)
        elif 400 <= self.status_code < 500:
            raise NotExistApi(self)
        else:
            self.raise_for_status()


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