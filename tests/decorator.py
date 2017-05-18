# coding=utf-8
from functools import wraps
from vcr import VCR
import os


def use_cassette(vcr=VCR(), path='fixtures/vcr_cassettes/', **kwargs):
    """
    Usage:
       @use_cassette()  # the default path will be fixtures/vcr_cassettes/foo.yaml
       def foo(self):
           ...

       @use_cassette(path='fixtures/vcr_cassettes/synopsis.yaml', record_mode='one')
       def foo(self):
           ...
    """

    def decorator(func):
        @wraps(func)
        def inner_func(*args, **kw):
            if os.path.isabs(path):
                file_path = path
            else:
                fun_path, fun_filename = os.path.split(func.__code__.co_filename)
                file_path = os.path.join(fun_path, path, os.path.splitext(fun_filename)[0])

            if not os.path.splitext(file_path)[1]:
                serializer = kwargs.get('serializer', vcr.serializer)
                file_path = os.path.join(file_path, '{0}.{1}'.format(func.__name__.lower(), serializer))

            with vcr.use_cassette(file_path, **kwargs):
                return func(*args, **kw)

        return inner_func

    return decorator