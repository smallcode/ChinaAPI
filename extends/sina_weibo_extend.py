# coding=utf-8
from chinaapi.sina_weibo import ApiClient


class ApiClientExtend(ApiClient):
    def prepare_url(self, segments, queries):
        url = super(ApiClientExtend, self).prepare_url(segments, queries)
        if 'like' in segments:
            # like操作需source和access_token参数，否则无法执行
            queries['source'] = self.app.key
            if not self.token.is_expires:
                queries['access_token'] = self.token.access_token
            return url.replace('weibo.com', 'weibo.cn')
        return url