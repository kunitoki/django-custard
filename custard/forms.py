# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.models import ContentType

from .conf import CUSTOM_WIDGETS_TYPES
from .utils import import_class


#==============================================================================
class CustomFieldModelBaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # additional form variables
        self.custom_classes = None

        # construct the form
        super(CustomFieldModelBaseForm, self).__init__(*args, **kwargs)
        
        # init custom fields from model in the form
        self.init_custom_fields()

    def clean(self):
        cleaned_data = super(CustomFieldModelBaseForm, self).clean()
        return cleaned_data

    def save(self, commit=True):
        self.instance = super(CustomFieldModelBaseForm, self).save(commit)
        if self.instance:
            self.instance.save()
        if not self.instance.pk:
            raise Exception("Cannot create an object for some reason")
        self.save_custom_fields()
        return self.instance

    def init_custom_fields(self):
        """
        Populate the ``form.fields[]`` with the additional fields coming from
        the custom fields models.
        """
        content_type = self.get_content_type()
        fields = self.get_fields_for_content_type(content_type)
        for f in fields:
            name = str(f.name)
            initial = f.initial
            self.fields[name] = f.get_form_field()
            self.fields[name].is_custom = True
            self.fields[name].required = f.required
            self.fields[name].widget = self.get_widget_for_field(f.data_type)
            if self.instance and self.instance.pk:
                value = self.search_value_for_field(f,
                                                    content_type,
                                                    self.instance.pk)
                if len(value) > 0:
                    initial = value[0].value
            self.fields[name].initial = self.initial[name] = initial

    def save_custom_fields(self):
        """
        Perform save and validation over the custom fields
        """
        content_type = self.get_content_type()
        fields = self.get_fields_for_content_type(content_type)
        for f in fields:
            name = str(f.name)
            fv = self.search_value_for_field(f,
                                             content_type,
                                             self.instance.pk)
            if len(fv) > 0:
                value = fv[0]
                value.value = self.cleaned_data[name]
            else:
                value = self.create_value_for_field(f,
                                                    self.instance.pk,
                                                    self.cleaned_data[name])
            value.save()

    def get_model(self):
        """
        Returns the actual model this ``ModelForm`` is referring to
        """
        return self._meta.model

    def get_content_type(self):
        """
        Returns the content type instance of the model this ``ModelForm`` is
        referring to
        """
        return ContentType.objects.get_for_model(self.get_model())

    def get_widget_for_field(self, fieldtype, attrs={}):
        """
        Returns the defined widget type instance built from the type of the field

        :param fieldtype: string referring to field types
        :param attrs: attributes of widgets
        :return: the widget instance
        """
        return import_class(CUSTOM_WIDGETS_TYPES[fieldtype])(**attrs)

    def get_fields_for_content_type(self, content_type):
        """
        Returns all fields for a given content type

        Example implementation:

          return MyCustomField.objects.filter(content_type=content_type)

        :param content_type: content type to search
        :return: the custom field instances
        """
        raise NotImplementedError

    def search_value_for_field(self, field, content_type, object_id):
        """
        This function will return the CustomFieldValue instance for a given
        field of an object that has the given content_type

        Example implementation:

          return MyCustomFieldValue.objects.filter(custom_field=field,
                                                   content_type=content_type,
                                                   object_id=object_id)

        :param field: the custom field instance
        :param content_type: the content type instance
        :param object_id: the object id this value is referring to
        :return: CustomFieldValue queryset
        """
        raise NotImplementedError

    def create_value_for_field(self, field, object_id, value):
        """
        Create a value for a given field of an object

        Example implementation:

          return MyCustomFieldValue(custom_field=field,
                                    object_id=object_id,
                                    value=value)

        :param field: the custom field instance
        :param object_id: the object id this value is referring to
        :param value: the value to set
        :return: the value instance (not saved!)
        """
        raise NotImplementedError
