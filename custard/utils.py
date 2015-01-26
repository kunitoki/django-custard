from __future__ import unicode_literals
from django.utils import importlib


#==============================================================================
def import_class(name):
    components = name.split('.')
    mod = importlib.import_module(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
