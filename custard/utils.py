# -*- coding: utf-8 -*-

import importlib
import functools
import warnings


#==============================================================================
def import_class(name):
    components = name.split('.')
    mod = importlib.import_module(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


#==============================================================================
def deprecate(msg, klass=PendingDeprecationWarning):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(msg, klass, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
