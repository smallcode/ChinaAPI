# coding=utf-8
import types
import requests
from .jsonDict import JsonDict
from .exceptions import ApiResponseValueError, NotExistApi


def json_dict(self):
    try:
        return self.json(object_hook=lambda pairs: JsonDict(pairs.iteritems()))
    except ValueError, e:
        if self.ok:
            raise ApiResponseValueError(self, e)
        else:
            raise NotExistApi(self)


def override_json(response, *args, **kwargs):
    response.json_dict = types.MethodType(json_dict, response)
    return response


class Request(object):
    def __init__(self):
        self._session = requests.session()
        self._session.hooks = dict(response=override_json)

    def _parse_response(self, response):
        return response.json_dict()