# coding=utf-8
class ApiError(StandardError):
    def __init__(self, request, code, message, sub_code='', sub_message=''):
        self.request = request
        self.code = code
        self.sub_code = sub_code
        self.sub_message = sub_message
        StandardError.__init__(self, message)

    def __str__(self):
        if self.sub_code or self.sub_message:
            return u'[{0}]: {1}, [{2}]: {3}, request: {4}'.format(str(self.code), self.message, str(self.sub_code),
                                                                  self.sub_message, self.request)
        return u'[{0}]: {1}, request: {2}'.format(str(self.code), self.message, self.request)


class ApiResponseError(ApiError):
    def __init__(self, response, code, message, sub_code='', sub_message=''):
        self.response = response
        super(ApiResponseError, self).__init__(self.get_request_url(), code, message, sub_code, sub_message)

    def get_request_url(self):
        if self.response.request.body:
            return '{0}?{1}'.format(self.response.url, self.response.request.body)
        return self.response.url


class ApiInvalidError(ApiError):
    def __init__(self, request, code=0, message='Invalid Api!'):
        super(ApiInvalidError, self).__init__(request, code, message)


class ApiNotExistError(ApiResponseError):
    def __init__(self, response, code=0, message='Request Api not found!'):
        if response.text:
            message = response.text
        if not code:
            code = response.status_code
        super(ApiNotExistError, self).__init__(response, code, message)