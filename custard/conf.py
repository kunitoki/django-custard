# -*- coding: utf-8 -*-

from django.conf import settings


CUSTOM_TYPE_TEXT     = 'text'
CUSTOM_TYPE_INTEGER  = 'int'
CUSTOM_TYPE_FLOAT    = 'float'
CUSTOM_TYPE_TIME     = 'time'
CUSTOM_TYPE_DATE     = 'date'
CUSTOM_TYPE_DATETIME = 'datetime'
CUSTOM_TYPE_BOOLEAN  = 'boolean'


CUSTOM_CONTENT_TYPES = getattr(settings, 'CUSTOM_CONTENT_TYPES', None)


CUSTOM_FIELD_TYPES = {
    CUSTOM_TYPE_TEXT:     'django.forms.fields.CharField',
    CUSTOM_TYPE_INTEGER:  'django.forms.fields.IntegerField',
    CUSTOM_TYPE_FLOAT:    'django.forms.fields.FloatField',
    CUSTOM_TYPE_TIME:     'django.forms.fields.TimeField',
    CUSTOM_TYPE_DATE:     'django.forms.fields.DateField',
    CUSTOM_TYPE_DATETIME: 'django.forms.fields.DateTimeField',
    CUSTOM_TYPE_BOOLEAN:  'django.forms.fields.BooleanField',
}

CUSTOM_FIELD_TYPES.update(getattr(settings, 'CUSTOM_FIELD_TYPES', {}))


CUSTOM_WIDGETS_TYPES = {
    CUSTOM_TYPE_TEXT:     'django.contrib.admin.widgets.AdminTextInputWidget',
    CUSTOM_TYPE_INTEGER:  'django.contrib.admin.widgets.AdminIntegerFieldWidget',
    CUSTOM_TYPE_FLOAT:    'django.contrib.admin.widgets.AdminIntegerFieldWidget',
    CUSTOM_TYPE_TIME:     'django.contrib.admin.widgets.AdminTimeWidget',
    CUSTOM_TYPE_DATE:     'django.contrib.admin.widgets.AdminDateWidget',
    CUSTOM_TYPE_DATETIME: 'django.contrib.admin.widgets.AdminSplitDateTime',
    CUSTOM_TYPE_BOOLEAN:  'django.forms.widgets.CheckboxInput',
}

CUSTOM_WIDGETS_TYPES.update(getattr(settings, 'CUSTOM_WIDGETS_TYPES', {}))
