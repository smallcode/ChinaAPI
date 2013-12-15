# coding=utf-8
import requests
from chinaapi.utils import jsonDict
from chinaapi.utils.exceptions import ApiResponseValueError, NotExistApi


class Response(object):
    def __init__(self, response):
        self.response = response

    def json(self):
        try:
            return jsonDict.loads(self.response.text)
        except ValueError, e:
            if self.response.ok:
                raise ApiResponseValueError(self.response, e)
            else:
                raise NotExistApi(self.response)


class Request(object):
    def __init__(self):
        self._session = requests.session()

    def _parse_response(self, response):
        return Response(response).json()

    @staticmethod
    def _parse_querystring(querystring):
        return dict([item.split('=') for item in querystring.split('&')])

    # @staticmethod
    # def dict_to_querystring(params):
    #     return '?' + '&'.join(['='.join([k, str(v)]) for k, v in params.items()])
