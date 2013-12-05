# coding=utf-8
class ApiError(StandardError):
    def __init__(self, request, code, msg, sub_code='', sub_msg=''):
        self.request = request
        self.code = code
        self.msg = msg
        self.sub_code = sub_code
        self.sub_msg = sub_msg
        StandardError.__init__(self, msg)

    def __str__(self):
        if self.sub_code or self.sub_msg:
            return u'[{0}]: {1}, [{2}]: {3}, request: {4}'.format(str(self.code), self.msg, str(self.sub_code),
                                                                  self.sub_msg, self.request)
        return u'[{0}]: {1}, request: {2}'.format(str(self.code), self.msg, self.request)