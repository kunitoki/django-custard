Configuration
=============

You can customize Django Custard behaviour by adding ``CUSTOM_*`` configuration variable to your Django project ``settings.py`` file.

Default values are the ones specified in examples.


Full example
------------

Configuration sample you can use as a start::

  # Django Custard configuration example

  CUSTOM_CONTENT_TYPES = (
    'mymodelname',
    'myothermodelname',
    'user',
    'group',
  )

  CUSTOM_FIELD_TYPES = {
    'text':     'django.forms.fields.CharField',
    'integer':  'django.forms.fields.IntegerField',
    'float':    'django.forms.fields.FloatField',
    'time':     'django.forms.fields.TimeField',
    'date':     'django.forms.fields.DateField',
    'datetime': 'django.forms.fields.DateTimeField',
    'boolean':  'django.forms.fields.BooleanField',
  }
    
  CUSTOM_WIDGETS_TYPES = {
    'text':     'django.contrib.admin.widgets.AdminTextInputWidget',
    'integer':  'django.contrib.admin.widgets.AdminIntegerFieldWidget',
    'float':    'django.contrib.admin.widgets.AdminIntegerFieldWidget',
    'time':     'django.contrib.admin.widgets.AdminTimeWidget',
    'date':     'django.contrib.admin.widgets.AdminDateWidget',
    'datetime': 'django.contrib.admin.widgets.AdminSplitDateTime',
    'boolean':  'django.forms.widgets.CheckboxInput',
  }


Constants
---------

There are some constants defined in ``custard.conf`` that hold the field type
names. These can't be changed::

  CUSTOM_TYPE_TEXT     = 'text'
  CUSTOM_TYPE_INTEGER  = 'int'
  CUSTOM_TYPE_FLOAT    = 'float'
  CUSTOM_TYPE_TIME     = 'time'
  CUSTOM_TYPE_DATE     = 'date'
  CUSTOM_TYPE_DATETIME = 'datetime'
  CUSTOM_TYPE_BOOLEAN  = 'boolean'


Parameters
----------

CUSTOM_CONTENT_TYPES
^^^^^^^^^^^^^^^^^^^^

Select which content types will have custom fields, the name is the lower model name as it is available in ContentType.model::

  CUSTOM_CONTENT_TYPES = (
    'mymodelname',
    'myothermodelname',
  )


CUSTOM_FIELD_TYPES
^^^^^^^^^^^^^^^^^^

It's possible to override which custom form fields are generated for each field type when the form is constructed::

  CUSTOM_FIELD_TYPES = {
    'text':     'app.forms.MySpecialCharField',
    'integer':  'app.forms.AnotherIntegerField',
  }


CUSTOM_WIDGETS_TYPES
^^^^^^^^^^^^^^^^^^^^

It's possible to override which custom form fields widgets are generated for each field type when the form is constructed::

  CUSTOM_WIDGETS_TYPES = {
    'time':     'app.forms.widgets.AdminTimeWidget',
    'date':     'app.forms.widgets.AdminDateWidget',
    'datetime': 'app.forms.widgets.AdminSplitDateTime',
  }


