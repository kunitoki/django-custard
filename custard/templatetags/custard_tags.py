#import pprint
from django import template

import logging
logger = logging.getLogger(__name__)


#===============================================================================
register = template.Library()


#===============================================================================
@register.simple_tag
def debug(value):
    """
        Simple tag to debug output a variable;

        Usage:
            {% debug request %}
    """
    print("%s %s: " % (type(value), value))
    print(dir(value))
    print('\n\n')
    return ''
