# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _

from .conf import *
from .utils import import_class


#==============================================================================
DEFAULT_VALIDATOR_VALUE = """
## Custom validator function here
#def validator(value, instance=None):
#    #raise Exception("Invalid value")
#    pass
"""


#==============================================================================
class CustomContentType:

    @staticmethod
    def create_fields(valid_content_types=Q(), base_model=models.Model):
        """
        This method will create a model which will hold field types defined
        at runtime for each ContentType.
        """
        class CustomContentTypeField(base_model):
            DATATYPE_CHOICES = (
                (CUSTOM_TYPE_TEXT,     _('text')),
                (CUSTOM_TYPE_INTEGER,  _('integer')),
                (CUSTOM_TYPE_FLOAT,    _('float')),
                (CUSTOM_TYPE_TIME,     _('time')),
                (CUSTOM_TYPE_DATE,     _('date')),
                (CUSTOM_TYPE_DATETIME, _('datetime')),
                (CUSTOM_TYPE_BOOLEAN,  _('boolean')),
            )
        
            VALID_CONTENT_TYPES = valid_content_types
        
            content_type = models.ForeignKey(ContentType,
                                             related_name='custom_fields',
                                             verbose_name=_('content type'),
                                             limit_choices_to=VALID_CONTENT_TYPES)
            name = models.CharField(_('name'), max_length=100, db_index=True)
            label = models.CharField(_('label'), max_length=100)
            data_type = models.CharField(_('data type'), max_length=8, choices=DATATYPE_CHOICES, db_index=True)
            help_text = models.CharField(_('help text'), max_length=200, blank=True, null=True)
            required = models.BooleanField(_('required'), default=False)
            searchable = models.BooleanField(_('searchable'), default=True)
            initial = models.CharField(_('initial'), max_length=200, blank=True, null=True)
            min_length = models.PositiveIntegerField(_('min length'), blank=True, null=True)
            max_length = models.PositiveIntegerField(_('max length'), blank=True, null=True)
            min_value = models.FloatField(_('min value'), blank=True, null=True)
            max_value = models.FloatField(_('max value'), blank=True, null=True)
        
            class Meta:
                #unique_together = ('content_type', 'name')
                verbose_name = _('custom field')
                verbose_name_plural = _('custom fields')
                abstract = True
        
            def save(self, *args, **kwargs):
                if self.required:
                    # TODO - must create values for all instances that have not
                    model = self.content_type.model_class()
                    print model.objects.values_list('pk', flat=True)
                    print self.field.filter(content_type=self.content_type)
                    objs = self.field.filter(content_type=self.content_type) \
                                     .exclude(object_id__in=model.objects.values_list('pk', flat=True))
                    for obj in objs:
                        print obj
                super(CustomContentTypeField, self).save(*args, **kwargs)
        
            def validate_unique(self, exclude=None):
                try:
                    # HACK - workaround django bug https://code.djangoproject.com/ticket/17582
                    ct = self.content_type
                except:
                    raise ValidationError({ NON_FIELD_ERRORS: (_('The content type has not been specified'),) })
                qs = self.__class__._default_manager.filter(
                    content_type=self.content_type,
                    name=self.name,
                )
                if not self._state.adding and self.pk is not None:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError({ NON_FIELD_ERRORS: (_('The content type instance already has this field'),) })
        
            def get_form_field(self):
                field_attrs = {
                    'label': self.label,
                    'help_text': self.help_text,
                    'required': self.required,
                }
                if self.data_type == CUSTOM_TYPE_TEXT:
                    #widget_attrs = {}
                    if self.min_length:
                        field_attrs['min_length'] = self.min_length
                    if self.max_length:
                        field_attrs['max_length'] = self.max_length
                    #    widget_attrs['maxlength'] = self.max_length
                    #field_attrs['widget'] = widgets.AdminTextInputWidget(attrs=widget_attrs)
                elif self.data_type == CUSTOM_TYPE_INTEGER:
                    if self.min_value: field_attrs['min_value'] = int(self.min_value)
                    if self.max_value: field_attrs['max_value'] = int(self.max_value)
                    #field_attrs['widget'] = spinner.IntegerSpinnerWidget(attrs=field_attrs)
                elif self.data_type == CUSTOM_TYPE_FLOAT:
                    if self.min_value: field_attrs['min_value'] = float(self.min_value)
                    if self.max_value: field_attrs['max_value'] = float(self.max_value)
                    #field_attrs['widget'] = spinner.SpinnerWidget(attrs=field_attrs)
                elif self.data_type == CUSTOM_TYPE_TIME:
                    #field_attrs['widget'] = date.TimePickerWidget()
                    pass
                elif self.data_type == CUSTOM_TYPE_DATE:
                    #field_attrs['widget'] = date.DatePickerWidget()
                    pass
                elif self.data_type == CUSTOM_TYPE_DATETIME:
                    #field_attrs['widget'] = date.DateTimePickerWidget()
                    pass
                elif self.data_type == CUSTOM_TYPE_BOOLEAN:
                    pass
                field_type = import_class(CUSTOM_FIELD_TYPES[self.data_type])
                return field_type(**field_attrs)
        
            def __unicode__(self):
                return "%s" % (self.name)

        return CustomContentTypeField


    @staticmethod
    def create_values(custom_field_model,
                      base_model=models.Model):
        """
        This method will create a model which will hold field values for
        field types of custom_field_model.
        """
        class CustomContentTypeFieldValue(base_model):
            custom_field = models.ForeignKey(custom_field_model,
                                             verbose_name=_('custom field'),
                                             related_name='field')
            content_type = models.ForeignKey(ContentType, editable=False,
                                             verbose_name=_('content type'),
                                             limit_choices_to=custom_field_model.VALID_CONTENT_TYPES)
            object_id = models.PositiveIntegerField(_('object id'), db_index=True)
            content_object = generic.GenericForeignKey('content_type', 'object_id')
        
            value_text = models.TextField(blank=True, null=True)
            value_integer = models.IntegerField(blank=True, null=True)
            value_float = models.FloatField(blank=True, null=True)
            value_time = models.TimeField(blank=True, null=True)
            value_date = models.DateField(blank=True, null=True)
            value_datetime = models.DateTimeField(blank=True, null=True)
            value_boolean = models.NullBooleanField(blank=True)
        
            def _get_value(self):
                return getattr(self, 'value_%s' % self.custom_field.data_type)
            def _set_value(self, new_value):
                setattr(self, 'value_%s' % self.custom_field.data_type, new_value)
            value = property(_get_value, _set_value)
    
            class Meta:
                #unique_together = ('custom_field', 'content_type', 'object_id')
                verbose_name = _('custom field value')
                verbose_name_plural = _('custom field values')
                abstract = True
        
            def save(self, *args, **kwargs):
                # save content type as user shouldn't be able to change it
                self.content_type = self.custom_field.content_type
                super(CustomContentTypeFieldValue, self).save(*args, **kwargs)
        
            def validate_unique(self, exclude=None):
                qs = self.__class__._default_manager.filter(
                    custom_field=self.custom_field,
                    content_type=self.custom_field.content_type,
                    object_id=self.object_id,
                )
                if not self._state.adding and self.pk is not None:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError({ NON_FIELD_ERRORS: (_('A value for this custom field already exists'),) })
        
            def __unicode__(self):
                return "%s(%s): %s" % (self.custom_field.name, self.object_id, self.value)
    
        return CustomContentTypeFieldValue


#==============================================================================
class CustomQ:
    """
    Bastract class that simulates the usage of Q objects when building complex
    queries that need to touch custom fields too.
    """

    def get_fields_model(self):
        raise NotImplementedError

    def get_values_model(self):
        raise NotImplementedError

    def query(self, model, search_data, custom_args={}):
        q = Q()
        content_type = ContentType.objects.get_for_model(model)
        custom_args = dict({ 'content_type': content_type, 'searchable': True }, **custom_args)
        custom = dict((s.name, s) for s in self.get_fields_model().objects.filter(**custom_args))
        for key, custom_field in custom.items():
            value_lookup = 'value_text' # TODO - search in other field types (not only text)
            value_lookup = '%s__%s' % (value_lookup, 'icontains')
            found = self.get_values_model().objects.filter(**{ 'custom_field': custom_field,
                                                               'content_type': content_type,
                                                               value_lookup: search_data })
            q = q & Q(**{ str('%s__in' % (model._meta.pk.name)): [f.object_id for f in found] })
        return q

