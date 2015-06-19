from __future__ import unicode_literals
from importlib import import_module

#==============================================================================
def import_class(name):
    components = name.split('.')
    mod = import_module(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
