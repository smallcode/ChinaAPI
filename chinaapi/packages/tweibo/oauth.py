##
## OAuth2 demo class
##
#  Wiki: https://github.com/upbit/tweibo-pysdk/wiki/OAuth2Handler
#
# [example]
#   oauth = OAuth2Handler()
#   oauth.set_app_key_secret(APP_KEY, APP_SECRET, CALLBACK_URL)
#   oauth.set_access_token(ACCESS_TOKEN)
#   oauth.set_openid(OPENID)

import time

class OAuth2Handler(object):
    def __init__(self, auth_url="https://open.t.qq.com/cgi-bin/oauth2/"):
        self.auth_url = auth_url
        self.app_key = None
        self.app_secret = None
        self.redirect_uri = None
        self.access_token = None
        self.expires = 0.0
        self.openid = None
        self.openkey = None

    def set_app_key_secret(self, app_key, app_secret, redirect_uri):
        self.app_key = str(app_key)
        self.app_secret = str(app_secret)
        self.redirect_uri = redirect_uri

    def set_access_token(self, access_token, expires_in=8035200):
        self.access_token = str(access_token)
        self.expires = int(time.time()) + float(expires_in)

    def set_openid(self, openid, openkey=None):
        self.openid = openid
        self.openkey = openkey

    def get_access_token_url(self):
        # https://open.t.qq.com/cgi-bin/oauth2/authorize?client_id=APP_KEY&response_type=token&redirect_uri=http://www.myurl.com/example
        return "%sauthorize?client_id=%s&response_type=%s&redirect_uri=%s" % (self.auth_url, self.app_key, "token", self.redirect_uri)

    def refresh_token_url(self, refresh_token):
        # https://open.t.qq.com/cgi-bin/oauth2/access_token?client_id=APP_KEY&grant_type=refresh_token&refresh_token=REFRESH_TOKEN
        return "%saccess_token?client_id=%s&grant_type=refresh_token&refresh_token=%s" % (self.auth_url, self.app_key, refresh_token)

    def get_oauth_params(self, clientip="10.0.0.1"):
        """ return http param for string """
        if (self.app_key == None) or (self.access_token == None) or (self.openid == None):
            raise Exception("app_key(%s) or access_token(%s) or openid(%s) miss!" % (self.app_key, self.access_token, self.openid))

        oauth2_string = "oauth_consumer_key=%s&access_token=%s&openid=%s&clientip=%s&oauth_version=2.a&scope=all" \
            % (self.app_key, self.access_token, self.openid, clientip)
        return oauth2_string
