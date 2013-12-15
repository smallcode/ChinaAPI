# coding=utf-8
import requests
from chinaapi.utils import jsonDict
from chinaapi.utils.exceptions import ApiResponseValueError, NotExistApi


class Response(object):
    def __init__(self, response):
        self.response = response

    @property
    def content(self):
        return self.response.content

    @property
    def text(self):
        return self.response.text

    def json(self):
        response = self.response
        try:
            return jsonDict.loads(response.text)
        except ValueError, e:
            if response.ok:
                raise ApiResponseValueError(response, e)
            else:
                raise NotExistApi(response)


class Request(object):
    def __init__(self):
        self._session = requests.session()

    def _parse_response(self, response):
        return Response(response).json()

    @staticmethod
    def querystring_to_dict(query_string):
        return dict([item.split('=') for item in query_string.split('&')])

    @staticmethod
    def dict_to_querystring(params):
        return '?' + '&'.join(['='.join([k, str(v)]) for k, v in params.items()])
