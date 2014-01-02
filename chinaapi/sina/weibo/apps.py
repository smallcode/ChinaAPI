# coding=utf-8
from chinaapi.open import App


class WeicoAndroidApp(App):
    """ Weico.Android版 """
    def __init__(self):
        super(WeicoAndroidApp, self).__init__('211160679', '63b64d531b98c2dbff2443816f274dd3')


class WeicoIphoneApp(App):
    """ Weico.Iphone版 """
    def __init__(self):
        super(WeicoIphoneApp, self).__init__('82966982', '72d4545a28a46a6f329c4f2b1e949e6a')
