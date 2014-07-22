# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .conf import (CUSTOM_TYPE_TEXT, CUSTOM_TYPE_INTEGER, CUSTOM_TYPE_FLOAT,
    CUSTOM_TYPE_TIME, CUSTOM_TYPE_DATE, CUSTOM_TYPE_DATETIME, CUSTOM_TYPE_BOOLEAN,
    CUSTOM_CONTENT_TYPES, CUSTOM_FIELD_TYPES)

from .utils import import_class


#==============================================================================
class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


#==============================================================================
class CustomContentType(object):

    def __init__(self):
        """
        Constructor
        """
        pass

    def create_fields(self, base_model=models.Model):
        """
        This method will create a model which will hold field types defined
        at runtime for each ContentType.
        """

        @python_2_unicode_compatible
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

            CONTENT_TYPES = Q(name__in=CUSTOM_CONTENT_TYPES)\
                if CUSTOM_CONTENT_TYPES is not None else Q()

            content_type = models.ForeignKey(ContentType,
                                             related_name='custom_fields',
                                             verbose_name=_('content type'),
                                             limit_choices_to=CONTENT_TYPES)
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
                super(CustomContentTypeField, self).save(*args, **kwargs)
        
            def validate_unique(self, exclude=None):
                # HACK - workaround django bug https://code.djangoproject.com/ticket/17582
                #try:
                #ct = self.content_type
                #except:
                #    raise ValidationError({ NON_FIELD_ERRORS: (_('The content type has not been specified'),) })

                # field name already defined in Model class
                model = self.content_type.model_class()
                if self.name in [f.name for f in model._meta.fields]:
                    raise ValidationError({ 'name': (_('Custom field already defined for content type %(model_name)s') % {'model_name': model.__name__},) })

                # field name already defined in custom fields for content type
                qs = self.__class__._default_manager.filter(
                    content_type=self.content_type,
                    name=self.name,
                )
                if not self._state.adding and self.pk is not None:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError({ 'name': (_('Custom field already defined content type %(model_name)s') % {'model_name': model.__name__},) })

                # if field is required must issue a initial value
                if self.required:
                    # TODO - must create values for all instances that have not
                    #print model.objects.values_list('pk', flat=True)
                    #print self.field.filter(content_type=self.content_type)
                    #objs = self.field.filter(content_type=self.content_type) \
                    #                 .exclude(object_id__in=model.objects.values_list('pk', flat=True))
                    #for obj in objs:
                    #    print obj
                    pass
        
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
        
            def __str__(self):
                return "%s" % (self.name)

        return CustomContentTypeField

    def create_values(self, custom_field_model, base_model=models.Model):
        """
        This method will create a model which will hold field values for
        field types of custom_field_model.
        """

        @python_2_unicode_compatible
        class CustomContentTypeFieldValue(base_model):
            custom_field = models.ForeignKey(custom_field_model,
                                             verbose_name=_('custom field'),
                                             related_name='field')
            content_type = models.ForeignKey(ContentType, editable=False,
                                             verbose_name=_('content type'),
                                             limit_choices_to=custom_field_model.CONTENT_TYPES)
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

                # TODO - here perform custom validation of value

            def __str__(self):
                return "%s(%s): %s" % (self.custom_field.name, self.object_id, self.value)
    
        return CustomContentTypeFieldValue

    def create_manager(self, fields_model, values_model):
        """
        This will create the custom Manager that will use the fields_model and values_model
        respectively.
        """
        fields_model = fields_model.split(".")
        values_model = values_model.split(".")
        
        class CustomManager(models.Manager):
            def get_fields_model(self):
                return get_model(fields_model[0], fields_model[1])
        
            def get_values_model(self):
                return get_model(values_model[0], values_model[1])
        
            def search(self, search_data, custom_args={}):
                """
                Search inside the custom fields for this model for any match
                 of search_data and returns existing model instances

                :param search_data:
                :param custom_args:
                :return:
                """
                qs = None
                content_type = ContentType.objects.get_for_model(self.model)
                custom_args = dict({ 'content_type': content_type, 'searchable': True }, **custom_args)
                custom = dict((s.name, s) for s in self.get_fields_model().objects.filter(**custom_args))
                for key, custom_field in custom.items():
                    value_lookup = 'value_text' # TODO - search in other field types (not only text)
                    value_lookup = '%s__%s' % (value_lookup, 'icontains')
                    found = self.get_values_model().objects.filter(**{ 'custom_field': custom_field,
                                                                       'content_type': content_type,
                                                                       value_lookup: search_data })
                    if found.count() > 0:
                        if qs is None:
                            qs = Q()
                        qs = qs & Q(**{ str('%s__in' % self.model._meta.pk.name): [f.object_id for f in found] })
                if qs is None:
                    return self.get_queryset().none()
                return self.get_queryset().filter(qs)

        return CustomManager()
        

#==============================================================================
custom = CustomContentType()
