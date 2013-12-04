ChinaAPI
=========================

安装
----

安装 ChinaAPI，最简单的方法:

.. code-block:: bash

    $ pip install chinaapi

注：chinaapi依赖外部模块requests: https://github.com/kennethreitz/requests

使用方法:
---------

新浪微博API的使用示例：

.. code-block:: python

        from chinaapi.sina_weibo import ApiClient
        from chinaapi.utils.models import App, Token


        # client的设置
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token')  # 填上取得的access_token
        client = ApiClient(app)
        client.set_access_token(token)

        # 获取用户信息，对应的接口是：users/show
        r = client.users.show(uid=1904178193)
        print r.name  # 显示用户昵称：微博开放平台

        # 发布带图片的微博，对应的接口是：statuses/upload
        pic = open('pic.jpg', 'rb')
        r = client.statuses.upload(status=u'发布的内容', pic=pic)
        print r.id  # 显示发布成功的微博的编号（即mid）：1234567890123456


新浪微博API的调用规则：**斜杠映射为点**

- users/show    ==>    client.users.show()
- statuses/upload     ==>    client.statuses.upload()


----


淘宝API的使用示例：

.. code-block:: python

        from chinaapi.taobao import ApiClient
        from chinaapi.utils.models import App


        # client的设置
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        client = ApiClient(app)

        # 获取淘宝客店铺列表，对应的接口是：taobao.tbk.shops.get
        r = self.client.tbk.shops.get(cid=14, fields='user_id,seller_nick,shop_title,pic_url')
        print len(r.tbk_shops_get_response.tbk_shops.tbk_shop)  # 显示店铺列表的数量：40


淘宝API的调用规则：直接映射（可省略前缀taobao.）

- taobao.itemcats.get    ==>    client.itemcats.get()  或者  client.taobao.itemcats.get()
- taobao.tbk.shops.get   ==>    client.tbk.shops.get()  或者  client.taobao.tbk.shops.get()

感谢以下Python SDK的开发者们的贡献：
-----------------------------------

- 新浪微博：https://github.com/michaelliao/sinaweibopy
- 腾讯微博：https://github.com/upbit/tweibo-pysdk
- 淘宝：https://github.com/sempr/taobaopy