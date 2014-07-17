# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.models import ContentType

#from nublas.library.utils.future import timeout


#==============================================================================
class CustomFieldModelBaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # if we have an instance then it's an edit
        if kwargs.has_key('instance'):
            self.instance = kwargs.get('instance')
        else:
            self.instance = None
        # force the form to display values even if they are empty
        # see template "asso/apps/base/templates/base/generic/field_view.html"
        self.empty_value_display = True
        # construct the form
        super(CustomFieldModelBaseForm, self).__init__(*args, **kwargs)
        # list custom fields from model
        content_type = self.get_content_type()
        fields = self.get_fields_for_content_type(content_type)
        for f in fields:
            name = str(f.name)
            self.fields[name] = f.get_form_field()
            self.fields[name].required = f.required
            initial = f.initial
            if self.instance:
                value = self.search_value_for_field(f,
                                                    content_type,
                                                    self.instance.pk)
                if len(value) > 0:
                    initial = value[0].value
            self.fields[name].initial = initial
            self.initial[name] = initial
        # HACK - Baseform method, it has been triggered with an empty self.fields, now retrigger
        #self._update_fields_widget()

    def clean(self):
        # default clean
        cleaned_data = super(CustomFieldModelBaseForm, self).clean()
        # clean custom fields from model
#        content_type = self.get_content_type()
#        fields = self.get_fields_for_content_type(content_type)
#        for f in fields:
#            name = str(f.name)
#            if cleaned_data.has_key(name):
#                value = cleaned_data[name]
#                if f.validator:
#                    func = f.validator_code.get('validator', None)
#                    if func:
#                        try:
#                            timeout(func, (value, self.instance), timeout_duration=f.validator_timeout)
#                        except Exception, arg:
#                            self._errors[name] = self.error_class([unicode(arg)])
#                            del cleaned_data[name]
        return cleaned_data

    def save(self, commit=True):
        self.instance = super(CustomFieldModelBaseForm, self).save(commit)
        if self.instance:
            self.instance.save()
        if not self.instance.pk:
            raise Exception("Cannot create an object for some reason")
            
        # save values
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
            
        return self.instance

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.get_model())

    def get_model(self):
        if not hasattr(self, 'Meta'):
            raise Exception("Must define a Meta class in your form")
        if not hasattr(self.Meta, 'model'):
            raise Exception("Your form Meta class must define a model")
        return self.Meta.model

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
