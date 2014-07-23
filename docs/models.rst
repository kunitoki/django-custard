Models
======

Rationale
---------

Django Custard comes with a series of internally defined models and classes that
tries to be as more unobtrusive as possible, so you can extend and make changes
to its internal models and classes, also by specifying in your explicit app::

  from django.db import models
  from custard.models import custom

  class CustomFieldsModel(custom.create_fields()):
      def foo(self):
          return "bar"

  class CustomValuesModel(custom.create_values(CustomFieldsModel)):
      class Meta:
          verbose_name = 'custom field value'
          verbose_name_plural = 'custom field values'


All models it creates are abstract base models that can also inherit from your
specific base model class. Think for example when you want all your models to
subclass of ``django_extensions.db.modelsTimeStampedModel``::

  from django.db import models
  from custard.models import custom
  from django_extensions.db.models import TimeStampedModel

  class CustomFieldsModel(custom.create_fields(base_model=TimeStampedModel)):
      pass

  class CustomValuesModel(custom.create_values(CustomFieldsModel, base_model=TimeStampedModel)):
      pass


Default for ``base_model`` is ``django.db.models.Model``


Mixin
-----

When building your models you can attach a special ``Mixin`` that implements
some helper functions to ease set and get custom field values::

  from django.db import models
  from custard.models import custom

  CustomMixin = custom.create_mixin('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')

  class Example(models.Model, CustomMixin):
      name = models.CharField(max_length=255)

  class CustomFieldsModel(custom.create_fields()):
      pass

  class CustomValuesModel(custom.create_values(CustomFieldsModel)):
      pass

The Mixin must know which classes are actually implementing the custom fields
definitions and the custom fields values, so ``custom.create_mixin`` you must
explicitly specify those model model with the full application label.

A number of methods are then added to your model:

``get_custom_fields(self)``
    Return a list of custom fields for this model

``get_custom_field(self, field_name)``
    Get a custom field object for this model

``get_custom_value(self, field_name)``
    Get a value for a specified custom field

``set_custom_value(self, field_name, value)``
    Set a value for a specified custom field


Manager
-------

In order to be able to search custom fields flagged as ``searchable`` in models,
you can create a special manager for your model needs::

  from django.db import models
  from custard.models import custom

  CustomManager = custom.create_manager('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')

  class Example(models.Model):
      name = models.CharField(max_length=255)

      objects = models.Manager()
      custom = CustomManager()

  class CustomFieldsModel(custom.create_fields()):
      pass

  class CustomValuesModel(custom.create_values(CustomFieldsModel)):
      pass


The Manager must know which classes are actually implementing the custom fields
definitions and the custom fields values, so ``custom.create_manager`` you must
explicitly specify those model model with the full application label.

This way you can add this special kind of manager even to your external apps.

Is then possible to execute the ``search`` method in the model, which will search
Example instances that contains the search string and returns a queryset much
like doing a filter call::

  qs = Example.custom.search('foobar')


It is also possible to use a specific Manager as base class for your custom
manager::

  from django.db import models
  from custard.models import custom

  class MyUberManager(models.Manager):
      def super_duper(self):
          return None

  CustomManager = custom.create_manager('myapp.CustomFieldsModel',
                                        'myapp.CustomValuesModel',
                                        base_manager=MyUberManager)

  class Example(models.Model):
      objects = CustomManager()

  Example.objects.super_duper()


.. warning::
   Be careful to always define a default_manager for you Model named ``objects``.
   If for some reason you omit to do so, you likely will end up in runtime errors
   when you use any class in Django Custard.


Using the models
----------------

It's possible to create fields on the fly for any model and create::

  from django.contrib.contenttypes.models import ContentType
  from custard.conf import CUSTOM_TYPE_TEXT
  from custard.models import custom

  from .models import Example, CustomFieldsModel, CustomValuesModel

  # First obtain the content type
  example_content_type = ContentType.objects.get_for_model(Example)

  # Create a text custom field
  custom_field = CustomFieldsModel.objects.create(content_type=example_content_type,
                                                  data_type=CUSTOM_TYPE_TEXT,
                                                  name='my_first_text_field',
                                                  label='My field',
                                                  searchable=False)
  custom_field.save()

  # Create a value for an instance of you model
  custom_value = CustomValuesModel.objects.create(custom_field=custom_field,
                                                  object_id=Example.objects.get(pk=1).pk)
  custom_value.value = "this is a custom value"
  custom_value.save()


