# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.models import ContentType

from .conf import CUSTOM_WIDGETS_TYPES
from .utils import import_class


#==============================================================================
class CustomFieldModelBaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.custom_classes = None

        # construct the form
        super(CustomFieldModelBaseForm, self).__init__(*args, **kwargs)
        
        # list custom fields from model
        content_type = self.get_content_type()
        fields = self.get_fields_for_content_type(content_type)
        for f in fields:
            name = str(f.name)
            self.fields[name] = f.get_form_field()
            self.fields[name].is_custom = True
            self.fields[name].required = f.required
            self.fields[name].widget = self.get_widget_for_field(f.data_type)
            initial = f.initial
            if self.instance and self.instance.pk:
                value = self.search_value_for_field(f,
                                                    content_type,
                                                    self.instance.pk)
                if len(value) > 0:
                    initial = value[0].value
            self.fields[name].initial = self.initial[name] = initial

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

    def save_custom_fields(self):
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

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.get_model())

    def get_model(self):
        if not hasattr(self, 'Meta'):
            raise Exception("Must define a Meta class in your form")
        if not hasattr(self.Meta, 'model'):
            raise Exception("Your form Meta class must define a model")
        return self.Meta.model

    def get_widget_for_field(self, fieldtype, attrs={}):
        return import_class(CUSTOM_WIDGETS_TYPES[fieldtype])(**attrs)

    def search_value_for_field(self, field, content_type, object_id):
        #return ContentTypeCustomFieldValue.objects.filter(custom_field=field,
        #                                                  content_type=content_type,
        #                                                  object_id=object_id)
        raise NotImplementedError

    def create_value_for_field(self, field, object_id, value):
        #return ContentTypeCustomFieldValue(custom_field=field,
        #                                   object_id=object_id,
        #                                   value=value)
        raise NotImplementedError

    def get_fields_for_content_type(self, content_type):
        #return ContentTypeCustomField.objects.filter(content_type=content_type)
        raise NotImplementedError
