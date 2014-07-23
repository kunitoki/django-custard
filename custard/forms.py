# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.models import ContentType

from .conf import (CUSTOM_TYPE_TEXT, CUSTOM_TYPE_INTEGER, CUSTOM_TYPE_FLOAT,
    CUSTOM_TYPE_TIME, CUSTOM_TYPE_DATE, CUSTOM_TYPE_DATETIME, CUSTOM_TYPE_BOOLEAN,
    CUSTOM_CONTENT_TYPES, CUSTOM_FIELD_TYPES, CUSTOM_WIDGETS_TYPES)
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
            self.fields[name] = self.get_formfield_for_field(f)
            self.fields[name].is_custom = True
            self.fields[name].required = f.required
            self.fields[name].widget = self.get_widget_for_field(f)
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

    def get_formfield_for_field(self, field):
        """
        Returns the defined formfield instance built from the type of the field

        :param field: custom field instance
        :return: the formfield instance
        """
        field_attrs = {
            'label': field.label,
            'help_text': field.help_text,
            'required': field.required,
        }
        if field.data_type == CUSTOM_TYPE_TEXT:
            #widget_attrs = {}
            if field.min_length:
                field_attrs['min_length'] = field.min_length
            if field.max_length:
                field_attrs['max_length'] = field.max_length
            #    widget_attrs['maxlength'] = field.max_length
            #field_attrs['widget'] = widgets.AdminTextInputWidget(attrs=widget_attrs)
        elif field.data_type == CUSTOM_TYPE_INTEGER:
            if field.min_value: field_attrs['min_value'] = int(float(field.min_value))
            if field.max_value: field_attrs['max_value'] = int(float(field.max_value))
            #field_attrs['widget'] = spinner.IntegerSpinnerWidget(attrs=field_attrs)
        elif field.data_type == CUSTOM_TYPE_FLOAT:
            if field.min_value: field_attrs['min_value'] = float(field.min_value)
            if field.max_value: field_attrs['max_value'] = float(field.max_value)
            #field_attrs['widget'] = spinner.SpinnerWidget(attrs=field_attrs)
        elif field.data_type == CUSTOM_TYPE_TIME:
            #field_attrs['widget'] = date.TimePickerWidget()
            pass
        elif field.data_type == CUSTOM_TYPE_DATE:
            #field_attrs['widget'] = date.DatePickerWidget()
            pass
        elif field.data_type == CUSTOM_TYPE_DATETIME:
            #field_attrs['widget'] = date.DateTimePickerWidget()
            pass
        elif field.data_type == CUSTOM_TYPE_BOOLEAN:
            pass
        field_type = import_class(CUSTOM_FIELD_TYPES[field.data_type])
        return field_type(**field_attrs)

    def get_widget_for_field(self, field, attrs={}):
        """
        Returns the defined widget type instance built from the type of the field

        :param field: custom field instance
        :param attrs: attributes of widgets
        :return: the widget instance
        """
        return import_class(CUSTOM_WIDGETS_TYPES[field.data_type])(**attrs)

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
