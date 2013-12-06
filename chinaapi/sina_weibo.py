# coding=utf-8
from .utils.clients import ApiClientBase, OAuth2Base, Method
from .utils.exceptions import ApiError
from furl import furl


class ApiClient(ApiClientBase):
    #写入接口
    post_methods = ['create', 'add', 'destroy', 'update', 'upload', 'repost', 'reply', 'send', 'post', 'invite',
                    'shield', 'order']
    #含下划线的写入接口，如：statuses/upload_url_text
    _post_methods = ['add', 'upload', 'destroy', 'update', 'set', 'cancel', 'not']

    def prepare_url(self, segments, queries):
        url = 'https://api.weibo.com/2/{0:s}.json'.format('/'.join(segments))
        if 'pic' in queries:
            return url.replace('https://api.', 'https://upload.api.')
        if 'remind' in segments:
            return url.replace('https://api.', 'https://rm.api.')
        return url

    def prepare_method(self, segments):
        segment = segments[-1].lower()
        if segment in self.post_methods or segment.split('_')[0] in self._post_methods:
            return Method.POST
        return Method.GET

    def prepare_headers(self, headers, queries):
        if self.token.is_expires:
            #对于不需要授权的API操作需追加source参数
            queries['source'] = self.app.key
        else:
            headers['Authorization'] = 'OAuth2 %s' % self.token.access_token
        return headers

    def prepare_body(self, queries):
        files = None
        if 'pic' in queries:
            files = dict(pic=(queries.pop('pic')))
        elif 'image' in queries:
            files = dict(image=(queries.pop('image')))
        return queries, files

    def parse_response(self, response):
        r = super(ApiClient, self).parse_response(response)
        if 'error_code' in r:
            raise ApiError(r.get('request', response.url), r.error_code, r.get('error', ''))
        return r


class OAuth2(OAuth2Base):
    def __init__(self, app):
        super(OAuth2, self).__init__(app, 'https://api.weibo.com/oauth2/')

    def authorize(self, **kwargs):
        if 'response_type' not in kwargs:
            kwargs['response_type'] = 'code'
        kwargs.update(client_id=self.app.key, redirect_uri=self.app.redirect_uri)
        return furl(self.url).join('authorize').set(args=kwargs).url

    def access_token(self, code):
        data = dict(client_id=self.app.key, client_secret=self.app.secret, grant_type='authorization_code',
                    code=code, redirect_uri=self.app.redirect_uri)
        r = self.session.post(self.url + 'access_token', data=data)

    def revoke(self):
        r = self.session.get(self.url + 'revokeoauth2')
        return r.result

