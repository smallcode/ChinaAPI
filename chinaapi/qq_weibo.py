# coding=utf-8
from .packages.tweibo.oauth import OAuth2Handler
from .packages.tweibo.tweibo import API, TWeiboError


OAuth2Handler = OAuth2Handler
ApiClient = API
ApiError = TWeiboError
