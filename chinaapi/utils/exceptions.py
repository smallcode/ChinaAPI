# coding=utf-8
class ApiError(Exception):
    def __init__(self, url, code, message, sub_code='', sub_message=''):
        self.url = url
        self.code = code
        self.message = message
        self.sub_code = sub_code
        self.sub_message = sub_message
        Exception.__init__(self, message)

    def __str__(self):
        if self.sub_code or self.sub_message:
            return u'[{0}]: {1}, [{2}]: {3}, request: {4}'.format(str(self.code), self.message, str(self.sub_code),
                                                                  self.sub_message, self.url)
        return u'[{0}]: {1}, request: {2}'.format(str(self.code), self.message, self.url)


class ApiResponseError(ApiError):
    def __init__(self, response, code, message, sub_code='', sub_message=''):
        self.response = response
        super(ApiResponseError, self).__init__(self.get_url(), code, message, sub_code, sub_message)

    def get_url(self):
        if self.response.request.body:
            return '{0}?{1}'.format(self.response.url, self.response.request.body)
        return self.response.url


class ApiResponseValueError(ApiResponseError):
    def __init__(self, response, value_error):
        super(ApiResponseValueError, self).__init__(response, response.status_code,
                                                    response.text if response.text else str(value_error))


class ApiInvalidError(ApiError):
    def __init__(self, url, code=0, message='Invalid Api!'):
        super(ApiInvalidError, self).__init__(url, code, message)


class ApiNotExistError(ApiResponseError):
    def __init__(self, response, code=0, message='Request Api not found!'):
        if response.text:
            message = response.text
        if not code:
            code = response.status_code
        super(ApiNotExistError, self).__init__(response, code, message)


class OAuth2Error(ApiError):
    def __init__(self, url, code, message):
        super(OAuth2Error, self).__init__(url, code, message)


class EmptyRedirectUriError(OAuth2Error):
    def __init__(self, url):
        super(EmptyRedirectUriError, self).__init__(url, 'OAuth2 request', 'Parameter absent: redirect_uri')