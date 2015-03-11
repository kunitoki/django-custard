from __future__ import unicode_literals
import sys
from django.conf import settings as django_settings
from django.utils.functional import cached_property as settings_property


#==============================================================================
# Do not cache properties when in test mode
if 'test' in sys.argv:
    settings_property = property


#==============================================================================
# Constants
CUSTOM_TYPE_TEXT     = 'text'
CUSTOM_TYPE_INTEGER  = 'integer'
CUSTOM_TYPE_FLOAT    = 'float'
CUSTOM_TYPE_TIME     = 'time'
CUSTOM_TYPE_DATE     = 'date'
CUSTOM_TYPE_DATETIME = 'datetime'
CUSTOM_TYPE_BOOLEAN  = 'boolean'


#==============================================================================
# Helper class for lazy settings
class LazySettingsDict(object):

    @settings_property
    def CUSTOM_CONTENT_TYPES(self):
        return getattr(django_settings, 'CUSTOM_CONTENT_TYPES', None)

    @settings_property
    def CUSTOM_FIELD_TYPES(self):
        return dict({
            CUSTOM_TYPE_TEXT:     'django.forms.fields.CharField',
            CUSTOM_TYPE_INTEGER:  'django.forms.fields.IntegerField',
            CUSTOM_TYPE_FLOAT:    'django.forms.fields.FloatField',
            CUSTOM_TYPE_TIME:     'django.forms.fields.TimeField',
            CUSTOM_TYPE_DATE:     'django.forms.fields.DateField',
            CUSTOM_TYPE_DATETIME: 'django.forms.fields.DateTimeField',
            CUSTOM_TYPE_BOOLEAN:  'django.forms.fields.BooleanField',
        }, **getattr(django_settings, 'CUSTOM_FIELD_TYPES', {}))

    @settings_property
    def CUSTOM_WIDGET_TYPES(self):
        return dict({
            CUSTOM_TYPE_TEXT:     'django.contrib.admin.widgets.AdminTextInputWidget',
            CUSTOM_TYPE_INTEGER:  'django.contrib.admin.widgets.AdminIntegerFieldWidget',
            CUSTOM_TYPE_FLOAT:    'django.contrib.admin.widgets.AdminIntegerFieldWidget',
            CUSTOM_TYPE_TIME:     'django.contrib.admin.widgets.AdminTimeWidget',
            CUSTOM_TYPE_DATE:     'django.contrib.admin.widgets.AdminDateWidget',
            CUSTOM_TYPE_DATETIME: 'django.contrib.admin.widgets.AdminSplitDateTime',
            CUSTOM_TYPE_BOOLEAN:  'django.forms.widgets.CheckboxInput',
        }, **getattr(django_settings, 'CUSTOM_WIDGET_TYPES', {}))


#==============================================================================
settings = LazySettingsDict()
