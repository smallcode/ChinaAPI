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
            return 'ApiError: {0:n}: {1:s}, {2:n}: {3:s}, request: {4:s}'.format(self.code, self.msg, self.sub_code,
                                                                                 self.sub_msg, self.request)
        return 'ApiError: {0:n}: {1:s}, request: {2:s}'.format(self.code, self.msg, self.request)