# coding=utf-8
class ApiError(IOError):
    """ API异常 """

    def __init__(self, url='', code=0, message='', sub_code=0, sub_message=''):
        self.url = url
        self.code = code
        self.message = message
        self.sub_code = sub_code
        self.sub_message = sub_message
        super(ApiError, self).__init__(code, message)

    @staticmethod
    def format(code, message):
        return '[%s]: %s, ' % (code, message) if code or message else ''

    def __str__(self):
        return '%s%srequest: %s' % (
            self.format(self.code, self.message), self.format(self.sub_code, self.sub_message), self.url)


class ApiRequestError(ApiError):
    def __init__(self, request, code, message, sub_code=0, sub_message=''):
        self.request = request
        super(ApiRequestError, self).__init__(self.get_url(), code, message, sub_code, sub_message)

    def is_multipart(self):
        return 'multipart/form-data' in self.request.headers.get('Content-Type', '')

    def get_url(self):
        if not self.is_multipart() and self.request.body:
            return '%s?%s' % (self.request.url, self.request.body)
        return self.request.url


class ApiResponseError(ApiRequestError):
    """ 响应结果中包含的异常 """

    def __init__(self, response, code=0, message='', sub_code=0, sub_message=''):
        self.response = response
        super(ApiResponseError, self).__init__(response.request,
                                               code or response.status_code,
                                               message or response.text,
                                               sub_code,
                                               sub_message)


class OAuth2Error(ApiError):
    """ OAuth2异常 """


class MissingRedirectUri(OAuth2Error, ValueError):
    """ 缺少 redirect_uri """