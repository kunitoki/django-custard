Models
======

Rationale
---------

Django Custard comes with a series of internally defined models and classes that
tries to be as more unobtrusive as possible, so to make it possible any kind of
extension and manipulation of its internal models and classes. This is possible
through the ``custard.builder.CustomFieldsBuilder`` class::

  from django.db import models
  from custard.builder import CustomFieldsBuilder

  builder = CustomFieldsBuilder('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')

  class CustomFieldsModel(builder.create_fields()):
      pass

  class CustomValuesModel(builder.create_values()):
      pass


The ``custard.builder.CustomFieldsBuilder`` must know which classes are actually
implementing the custom fields definitions and the custom fields values, so to
``custard.builder.CustomFieldsBuilder.__init__`` must be explicitly specified those
models as strings with the full application label, much like when implementing
``django.models.fields.ForeignKey`` for externally defined models.

The Django Custard models that implement custom fields and values are explicitly
declared as abstract, and not defined anywhere statically in the code. So it's
possible to implement them in any project, and even have multiple instances of
them, for example when it's needed to maintain custom fields separation inside
big apps.

When an application makes use of a standard base model for all its models, like
when subclassing from ``django_extensions.db.models.TimeStampedModel``, Django
Custard models can be constructed with a ``base_model`` class::

  from django.db import models
  from custard.builder import CustomFieldsBuilder
  from django_extensions.db.models import TimeStampedModel

  builder = CustomFieldsBuilder('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')

  class CustomFieldsModel(custom.create_fields(base_model=TimeStampedModel)):
      pass

  class CustomValuesModel(custom.create_values(base_model=TimeStampedModel)):
      pass


Default for ``base_model`` is ``django.db.models.Model``.


Manager
-------

In order to be able to search custom fields flagged as ``searchable`` in models,
it's possible to add a special manager for any model needs::

  from django.db import models
  from custard.builder import CustomFieldsBuilder

  builder = CustomFieldsBuilder('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')
  CustomManager = builder.create_manager()

  class Example(models.Model):
      name = models.CharField(max_length=255)

      objects = CustomManager()

  class CustomFieldsModel(builder.create_fields()):
      pass

  class CustomValuesModel(builder.create_values()):
      pass


Executing the ``search`` method in the model will then search Example instances
that contains the search string in any searchable custom field defined for that
model and returns a queryset much like doing a filter call::

  qs = Example.custom.search('foobar')


By passing a specific Manager class as ``base_manager`` parameter, the custom
manager will then inherit from that base class::

  from django.db import models
  from custard.builder import CustomFieldsBuilder

  builder = CustomFieldsBuilder('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')

  class MyUberManager(models.Manager):
      def super_duper(self):
          return None

  CustomManager = builder.create_manager(base_manager=MyUberManager)

  class Example(models.Model):
      objects = CustomManager()

  Example.objects.super_duper()


.. warning::
   Be careful to always define a default_manager named ``objects`` for any Model.
   If for some reason you omit to do so, you likely will end up in runtime errors
   when you use any class in Django Custard.


Using the models
----------------

It's possible to create fields on the fly for any model::

  from django.contrib.contenttypes.models import ContentType
  from custard.conf import CUSTOM_TYPE_TEXT

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
                                                  object_id=Example.objects.get(pk=1).pk,
                                                  value="this is a custom value")
  custom_value.save()


Mixin
-----

Custom fields and values attach to an application *real* models. To ease the
interaction with custom fields, it's possible to attach a special model ``Mixin`` to
any model for which it is possible to attach custom fields, and gain a simplified
interface to query and set fields and values::

  from django.db import models
  from custard.builder import CustomFieldsBuilder

  builder = CustomFieldsBuilder('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')
  CustomMixin = builder.create_mixin()

  class Example(models.Model, CustomMixin):
      name = models.CharField(max_length=255)

  class CustomFieldsModel(builder.create_fields()):
      pass

  class CustomValuesModel(builder.create_values()):
      pass

A number of methods are then added to your model:

``get_custom_fields(self)``
    Return a list of custom fields for this model

``get_custom_value(self, field_object)``
    Get a value for a specified custom field

``set_custom_value(self, field_object, value)``
    Set a value for a specified custom field

Look at this example::

  # First obtain the content type
  example_content_type = ContentType.objects.get_for_model(Example)

  # Create a fields for the content type
  custom_field = CustomFieldsModel.objects.create(content_type=example_content_type,
                                                  data_type=CUSTOM_TYPE_TEXT,
                                                  name='a_text_field',
                                                  label='My field',
                                                  searchable=True)
  custom_field.save()

  # Create an model instance
  obj = Example(name='hello')
  obj.save()

  # Set a custom field value
  obj.set_custom_value(custom_field, 'world')

