ChinaAPI
=========================

目前已引入的API Python SDK：
---------------------------

- 新浪微博：https://github.com/michaelliao/sinaweibopy
- 腾讯微博：https://github.com/upbit/tweibo-pysdk
- 淘宝：https://github.com/sempr/taobaopy


安装
----

安装 ChinaAPI，最简单的方法:

.. code-block:: bash

    $ pip install chinaapi

注：chinaapi依赖外部模块requests: https://github.com/kennethreitz/requests

使用方法:
--------

新浪微博的使用：

.. code-block:: python

        from chinaapi.sina_weibo import ApiClient
        from chinaapi.utils import models

        # client的设置
        app = models.App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = models.Token('access_token')  # 填上取得的access_token
        client = ApiClient(app)
        client.set_access_token(token)

        # 获取用户信息，对应的接口是：users/show
        r = client.users.show(uid=1904178193)
        print r.name  # 显示用户昵称：微博开放平台

        # 发布带图片的微博，对应的接口是：statuses/upload
        pic = open('pic.jpg', 'rb')
        r = client.statuses.upload(status=u'发布的内容', pic=pic)
        print r.id  # 显示发布成功的微博的编号（即mid）：1234567890123456


调用规则: 斜杠映射为点

- users/show    ==>    client.users.show()
- statuses/upload     ==>    client.statuses.upload()