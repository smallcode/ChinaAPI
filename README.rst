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


TODO:
----
现在只是直接调用外部包，将逐渐抽取共用的代码进行集成。

- HTTP部分统一使用requests: https://github.com/kennethreitz/requests
- 提取APIError基类
- 提取APIClient基类

