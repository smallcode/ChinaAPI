# coding=utf-8
from .utils.api import OAuth2


class ApiOAuth2(OAuth2):
    def __init__(self, app):
        super(ApiOAuth2, self).__init__(app, 'http://www.douban.com/service/auth/')

    def _get_access_token_url(self):
        return self.url + 'request_token'

        # def add(request):
        #     uid = request.session.get('uid', default = None)
        #     if uid is not None:
        #         request_token_url = 'http://www.douban.com/service/auth/request_token'
        #         authorize_url = 'http://www.douban.com/service/auth/authorize'
        #
        #         consumer = oauth.Consumer(DOUBAN_KEY, DOUBAN_SECRET)
        #         client = oauth.Client(consumer)
        #
        #         resp, content = client.request(request_token_url, "GET")
        #
        #         request_token = dict(urlparse.parse_qsl(content))
        #         request.session['rt_ot'] = request_token['oauth_token']
        #         request.session['rt_ots'] = request_token['oauth_token_secret']
        #
        #         red_url = "%s?oauth_token=%s&oauth_callback=%s" % (authorize_url, request_token['oauth_token'], BASE_URL+"/datasources/douban_callback")
        #         return redirect(red_url)
        #     else:
        #         return redirect('/login')
        #
        # def callback(request):
        #
        #     oauth_verifier = request.GET['oauth_token']
        #     access_token_url = 'http://www.douban.com/service/auth/access_token'
        #
        #     consumer = oauth.Consumer(DOUBAN_KEY, DOUBAN_SECRET)
        #     token = oauth.Token(request.session['rt_ot'], request.session['rt_ots'])
        #     token.set_verifier(oauth_verifier)
        #     client = oauth.Client(consumer, token)
        #
        #     resp, content = client.request(access_token_url, "POST")
        #     access_token = dict(urlparse.parse_qsl(content))
        #
        #     uid = request.session.get('uid', default = None)
        #     if uid is not None:
        #         p = Profile.objects.get(pk = uid)
        #
        #         token = oauth.Token(key=access_token['oauth_token'], secret=access_token['oauth_token_secret'])
        #         client = oauth.Client(consumer, token)
        #
        #         url = "http://api.douban.com/people/%s?alt=json" % (access_token['douban_user_id'])
        #         resp, content = client.request(url, "GET")
        #         user_info = JSONDecoder().decode(content)
        #
        #         en_info = JSONEncoder().encode(access_token)
        #         d = DataSource.objects.create(source_name="douban", auth_info=en_info, account_name=user_info['title']['$t'], owner=p)
        #         sync_source(d)
        #         return redirect('/datasources')
        #     else:
        #         return redirect('/login')


