# coding=utf-8
from functools import wraps


def retry(max_tries, exceptions=(Exception,), hook=None):
    """Retry calling the decorated function
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            tries = max_tries
            while tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    if hook is not None:
                        hook(e)
                    tries -= 1
            return f(*args, **kwargs)

        return f_retry  # true decorator
    return deco_retry