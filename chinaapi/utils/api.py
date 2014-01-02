# coding=utf-8
import requests
import types
from requests.models import PreparedRequest
from chinaapi.utils.jsonDict import JsonDict
from chinaapi.utils.exceptions import ApiResponseValueError, NotExistApi


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

    @classmethod
    def _parse_querystring(cls, querystring):
        return dict([item.split('=') for item in querystring.split('&')])

    @classmethod
    def _request_url(cls, url, params):
        pre = PreparedRequest()
        pre.prepare_url(url, params)
        return pre.url