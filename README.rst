ChinaAPI
=========================

.. image:: https://travis-ci.org/smallcode/ChinaAPI.png
    :target: https://travis-ci.org/smallcode/ChinaAPI

.. image:: https://badge.fury.io/py/chinaapi.png
    :target: http://badge.fury.io/py/chinaapi


ChinaAPI是一个API库，使用Python编写。

目前国内的几大开放平台，有新浪微博，腾讯微博，淘宝、人人、豆瓣等。
针对这几个平台，用Python语言编写的API库都比较独立，各具特色。
但仔细分析，不难发现这些库存在大量可通用的模块，并可抽象出统一的调用接口。
ChinaAPI就是为此目的而存在。

安装
----

安装 ChinaAPI，最简单的方法:

.. code-block:: bash

    $ pip install chinaapi

注：ChinaAPI使用： `Requests`_  （Http请求模块）和 `Furl`_ （Url组装模块）

----

新浪微博API:
------------

使用方法：

.. code-block:: python

        from chinaapi.sina_weibo import ApiClient, ApiOAuth2
        from chinaapi.utils.models import App, Token

        # 设置App
        # 填上自己的app_key，app_secret；redirect_uri可不填
        app = App('app_key', 'app_secret', 'redirect_uri')

        # 获取授权链接
        oauth2 = ApiOAuth2(app)
        url = oauth2.authorize()  # 如果app中未设置redirect_uri，则此处必须传入
        print url # 显示授权链接（该url用于提供给用户进行登录授权，授权成功后会回调redirect_uri?code=****）

        # 获取Token
        token = oauth2.access_token(code='code')  #  code取自回调地址后所附的code参数
        print token.access_token  # 显示访问令牌
        print token.expires_in  # 显示令牌剩余授权时间的秒数
        print token.expired_at  # 显示令牌到期日期，为timestamp格式

        # 设置ApiClient
        client = ApiClient(app)
        client.set_token(token)  # 使用上面取得的token，也可以另外自定义一个：token=Token('access_token')

        # 获取用户信息，对应的接口是：users/show
        r = client.users.show(uid=1904178193)
        print r.name  # 显示用户名

        # 发布带图片的微博，对应的接口是：statuses/upload
        pic = open('pic.jpg', 'rb')
        r = client.statuses.upload(status=u'发布的内容', pic=pic)
        print r.id  # 显示发布成功的微博的编号（即mid）：1234567890123456


调用规则：**斜杠（/）映射为点（.）**   

====================================== =========================================
            新浪微博API                               调  用
====================================== =========================================
  users/show                           client.users.show()
  statuses/upload                      client.statuses.upload()

====================================== =========================================

附：`新浪微博API文档`_

----

淘宝API:
------------


使用示例：

.. code-block:: python

        from chinaapi.taobao import ApiClient
        from chinaapi.utils.models import App


        # client的设置
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        client = ApiClient(app)

        # 获取淘宝客店铺列表，对应的接口是：taobao.tbk.shops.get
        # 返回结果r是json中tbk_shops_get_response的值，所有的接口都直接返回response（键名为：接口+_response后缀）的值
        r = client.tbk.shops.get(cid=14, fields='user_id,seller_nick,shop_title,pic_url')
        print len(r.tbk_shops.tbk_shop)  # 显示店铺列表的数量：40


调用规则：**直接映射（可省略前缀taobao.）**

====================================== =========================================
               淘宝API                               调  用
====================================== =========================================
  taobao.itemcats.get                  client.itemcats.get()  
                                       或者 client.taobao.itemcats.get()
  taobao.tbk.shops.get                 client.tbk.shops.get()  
                                       或者 client.taobao.tbk.shops.get()

====================================== =========================================

附：`淘宝API文档`_

----

腾讯微博API:
------------

使用方法：

.. code-block:: python

        from chinaapi.qq_weibo import ApiClient
        from chinaapi.utils.models import App, Token


        # client的设置
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token')       # 填上取得的access_token
        openid = 'openid'                   # 填上取得的openid
        client = ApiClient(app)
        client.set_token(token)
        client.set_openid(openid)

        # 获取当前登录用户的信息，对应的接口是：user/info
        # 返回结果r是json中的data值
        r = client.user.info()
        print r.name  # 显示用户名

        # 发布一条带图片的微博，对应的接口是：t/add_pic
        pic = open('pic.jpg', 'rb')
        r = client.t.add_pic(content=u'发布的内容', pic=pic)
        print r.id  # 显示微博的ID

        # 删除一条微博，对应的接口是：t/del
        r = client.t.delete(id=r.id)  # 请将del替换为delete
        print r.id  # 显示微博的ID

        # 有两种设置clientip的方法：
        # 1.全局设置，在该client所发起的所有调用中有效
        client.set_clientip('220.181.111.85')
        # 2.临时设置，只在此次调用中有效，会覆盖全局设置
        client.t.upload_pic(pic=pic, pic_type=2, clientip='220.181.111.85')


调用规则：**斜杠（/）映射为点（.），del映射为delete（因del是Python保留字，无法作为方法名）**   

====================================== =========================================
            腾讯微博API                               调  用
====================================== =========================================
  user/info                            client.user.info()
  t/add_pic                            client.t.add_pic()
  t/del                                client.t.delete()
====================================== =========================================

附：`腾讯微博API文档`_

----

人人API:
------------

使用方法：

.. code-block:: python

        from chinaapi.renren import ApiClient
        from chinaapi.utils.models import App, Token


        # client的设置
        app = App('app_key', 'app_secret')  # 填上自己的app_key，app_secret
        token = Token('access_token')  # 填上取得的access_token
        client = ApiClient(app)
        client.set_token(token)

        # 获取用户信息，对应的接口是：/v2/user/get
        r = client.user.get(userId=334258249)
        print r.name  # 显示用户名

        # 上传照片至用户相册，对应的接口是：/v2/photo/upload
        file = open('pic.jpg', 'rb')
        r = client.photo.upload(file=file)
        print r.id  # 显示照片的ID


调用规则：**斜杠（/）映射为点（.）**

====================================== =========================================
            人人API                               调  用
====================================== =========================================
  /v2/user/get                         client.user.get()
  /v2/photo/upload                     client.photo.upload()

====================================== =========================================

附：`人人API文档`_

----

TODO：
-----------------------------------

- 添加OAuth2说明

感谢以下Python SDK的开发者们的贡献：
-----------------------------------

- 新浪微博：`sinaweibopy`_
- 腾讯微博：`tweibo`_
- 淘宝：`taobaopy`_

.. _`sinaweibopy`: https://github.com/michaelliao/sinaweibopy
.. _`tweibo`: https://github.com/upbit/tweibo-pysdk
.. _`taobaopy`: https://github.com/sempr/taobaopy
.. _`Requests`: https://github.com/kennethreitz/requests
.. _`Furl`: https://github.com/gruns/furl
.. _`新浪微博API文档`: http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI
.. _`淘宝API文档`: http://open.taobao.com/doc/category_list.htm?spm=0.0.0.0.MNfatw&id=102
.. _`腾讯微博API文档`: http://wiki.open.t.qq.com/index.php/API%E6%96%87%E6%A1%A3
.. _`人人API文档`: http://wiki.dev.renren.com/wiki/API2
