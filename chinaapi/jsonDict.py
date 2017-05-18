# coding=utf-8
import json


class JsonDict(dict):
    """
    General json object that allows attributes to be bound to and also behaves like a dict.

    >>> jd = JsonDict(a=1, b='test')
    >>> jd.a
    1
    >>> jd.b
    'test'
    >>> jd['b']
    'test'
    >>> jd.c
    Traceback (most recent call last):
      ...
    AttributeError: 'JsonDict' object has no attribute 'c'
    >>> jd['c']
    Traceback (most recent call last):
      ...
    KeyError: 'c'
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def loads(string):
    """
    Parse json string into JsonDict.

    >>> r = loads(r'{"name":"Michael","score":95}')
    >>> r.name
    u'Michael'
    >>> r['score']
    95
    """
    return json.loads(string, object_hook=lambda pairs: JsonDict(iter(pairs.items())))