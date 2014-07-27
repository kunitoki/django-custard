Admin
=====

Editing fields
--------------

It's possible to edit fields for custom content types by registering a model admin for it::

  from django.contrib import admin

  from .models import CustomFieldsModel, CustomValuesModel

  class CustomFieldsModelAdmin(admin.ModelAdmin):
      pass
  admin.site.register(CustomFieldsModel, CustomFieldsModelAdmin)

  # Same goes for editing values
  class CustomValuesModelAdmin(admin.ModelAdmin):
      pass
  admin.site.register(CustomValuesModel, CustomValuesModelAdmin)


The form subclass
-----------------

First steps to integrate Django Custard with an app admin site is to create a
subclass of ``custard.forms.CustomFieldModelBaseForm`` and implements 3 functions namely:

``get_fields_for_content_type(self, content_type)``
    This function will return all fields defined for a specific content type

``search_value_for_field(self, field, content_type, object_id)``
    This function will return a custom value instance of the given field of a given content type object

``create_value_for_field(self, field, object_id, value)``
    This function will create a value of the given field of a given content type object

Here is an example::

  from django.contrib import admin
  from custard.forms import CustomFieldModelBaseForm

  from .models import Example, CustomFieldsModel, CustomValuesModel

  class ExampleForm(CustomFieldModelBaseForm):
      class Meta:
          model = Example

      # Returns all fields for a content type
      def get_fields_for_content_type(self, content_type):
          return CustomFieldsModel.objects.filter(content_type=content_type)

      # Returns the value for this field of a content type object
      def search_value_for_field(self, field, content_type, object_id):
          return CustomValuesModel.objects.filter(custom_field=field,
                                                  content_type=content_type,
                                                  object_id=object_id)

      # Create a value for this field of a content type object
      def create_value_for_field(self, field, object_id, value):
          return CustomValuesModel(custom_field=field,
                                   object_id=object_id,
                                   value=value)


ModelAdmin
----------

In admin site, add this new form as the default for for a ``ModelAdmin`` of any
model::

  class ExampleAdmin(admin.ModelAdmin):
      form = ExampleForm

  admin.site.register(Example, ExampleAdmin)


Then the last step is to subclass a model ``change_form.html`` and use the
Django Custard modified version:

``templates/admin/myapp/example/change_form.html``::

  {% extends "custard/admin/change_form.html" %}


Then editing ``Example`` object custom fields is enabled in the admin site.


Searches in list_view
---------------------

In order to enable search custom fields in admin in ``search_fields``, only
overriding ``ModelAdmin.get_search_results`` is needed::

  class ExampleAdmin(admin.ModelAdmin):
      form = ExampleForm

      def get_search_results(self, request, queryset, search_term):
          queryset, use_distinct = super(ExampleAdmin, self).get_search_results(request,
                                                                                queryset,
                                                                                search_term)
          queryset |= self.model.objects.search(search_term)
          return queryset, use_distinct

  admin.site.register(Example, ExampleAdmin)


.. note::
    This implies you have overridden your default ``objects`` manager in ``Example`` model
    with the manager that comes with Django Custard.

