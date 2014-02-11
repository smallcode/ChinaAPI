# coding=utf-8
import chinaapi


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'chinaapi',
    'chinaapi.douban',
    'chinaapi.qq',
    'chinaapi.qq.weibo',
    'chinaapi.renren',
    'chinaapi.sina',
    'chinaapi.sina.weibo',
    'chinaapi.taobao',
    'chinaapi.sohu',
    'chinaapi.netease',
]

requires = [
    'requests >= 2.1.0',
    'rsa >= 3.1.2',
]

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(
    name='chinaapi',
    version=chinaapi.__version__,
    description='Python SDK For China API: Sina Weibo, QQ Weibo, Taobao, Renren, Douban',
    long_description=readme + '\n\n' + history,
    author='smallcode',
    author_email='45945756@qq.com',
    url='https://github.com/smallcode/ChinaAPI',
    packages=packages,
    package_dir={'chinaapi': 'chinaapi'},
    include_package_data=True,
    install_requires=requires,
    license=chinaapi.__license__,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

