from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .conf import (CUSTOM_TYPE_TEXT, CUSTOM_TYPE_INTEGER, CUSTOM_TYPE_FLOAT,
    CUSTOM_TYPE_TIME, CUSTOM_TYPE_DATE, CUSTOM_TYPE_DATETIME, CUSTOM_TYPE_BOOLEAN,
    settings)


#==============================================================================
class CustomFieldsBuilder(object):
    """

    """

    def __init__(self, fields_model, values_model,
                 custom_content_types=settings.CUSTOM_CONTENT_TYPES):
        """

        :param fields_model:
        :param values_model:
        :return:
        """

        # TODO - validate fields_model / values_model strings

        self.fields_model = fields_model.split(".")
        self.values_model = values_model.split(".")
        self.custom_content_types = custom_content_types

        self.content_types_query = Q(name__in=self.custom_content_types) \
            if self.custom_content_types is not None else Q()


    @property
    def fields_model_class(self):
        return get_model(self.fields_model[0], self.fields_model[1])


    @property
    def values_model_class(self):
        return get_model(self.values_model[0], self.values_model[1])


    def create_fields(self, base_model=models.Model):
        """
        This method will create a model which will hold field types defined
        at runtime for each ContentType.

        :param base_model:
        :return:
        """

        CONTENT_TYPES =  self.content_types_query

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

            def clean(self):
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

            def validate_unique(self, exclude=None):
                # field name already defined in Model class
                model = self.content_type.model_class()
                if self.name in [f.name for f in model._meta.fields]:
                    raise ValidationError({ 'name': (_('Custom field already defined as model field for content type %(model_name)s') % {'model_name': model.__name__},) })

                # field name already defined in custom fields for content type
                qs = self.__class__._default_manager.filter(
                    content_type=self.content_type,
                    name=self.name,
                )
                if not self._state.adding and self.pk is not None:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError({ 'name': (_('Custom field already defined for content type %(model_name)s') % {'model_name': model.__name__},) })

            def __str__(self):
                return "%s" % self.name

        return CustomContentTypeField


    def create_values(self, base_model=models.Model):
        """
        This method will create a model which will hold field values for
        field types of custom_field_model.

        :param custom_field_model:
        :param base_model:
        :return:
        """

        _builder = self

        @python_2_unicode_compatible
        class CustomContentTypeFieldValue(base_model):
            custom_field = models.ForeignKey('.'.join(_builder.fields_model),
                                             verbose_name=_('custom field'),
                                             related_name='field')
            content_type = models.ForeignKey(ContentType, editable=False,
                                             verbose_name=_('content type'),
                                             limit_choices_to=_builder.content_types_query)
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

            def __str__(self):
                return "%s(%s): %s" % (self.custom_field.name, self.object_id, self.value)

        return CustomContentTypeFieldValue


    def create_manager(self, base_manager=models.Manager):
        """
        This will create the custom Manager that will use the fields_model and values_model
        respectively.

        :return:
        """

        _builder = self

        class CustomManager(base_manager):
            """

            :param base_manager:
            :return:
            """

            def search(self, search_data, custom_args={}):
                """
                Search inside the custom fields for this model for any match
                 of search_data and returns existing model instances

                :param search_data:
                :param custom_args:
                :return:
                """
                query = None
                content_type = ContentType.objects.get_for_model(self.model)
                custom_args = dict({ 'content_type': content_type, 'searchable': True }, **custom_args)
                custom_fields = dict((f.name, f) for f in _builder.fields_model_class.objects.filter(**custom_args))
                for key, f in custom_fields.items():
                    # TODO - search in other field types (not only text)
                    value_lookup = 'value_text'
                    value_lookup = '%s__%s' % (value_lookup, 'icontains')
                    found = _builder.values_model_class.objects.filter(**{ 'custom_field': f,
                                                                           'content_type': content_type,
                                                                           value_lookup: search_data })
                    if found.count() > 0:
                        if query is None:
                            query = Q()
                        query = query & Q(**{ str('%s__in' % self.model._meta.pk.name):
                                              [obj.object_id for obj in found] })
                if query is None:
                    return self.get_queryset().none()
                return self.get_queryset().filter(query)

        return CustomManager


    def create_mixin(self):
        """

        :return:
        """

        _builder = self

        class CustomModelMixin(object):
            @cached_property
            def _content_type(self):
                return ContentType.objects.get_for_model(self.__class__)

            def get_custom_fields(self):
                """ Return a list of custom fields for this model """
                return _builder.fields_model_class.objects.filter(content_type=self._content_type)

            def get_custom_field(self, field_name):
                """ Get a custom field object for this model """
                return _builder.fields_model_class.objects.get(name=field_name,
                                                               content_type=self._content_type)

            def get_custom_value(self, field_name):
                """ Get a value for a specified custom field """
                return _builder.values_model_class.objects.get(custom_field__name=field_name,
                                                               content_type=self._content_type,
                                                               object_id=self.pk).value

            def set_custom_value(self, field_name, value):
                """ Set a value for a specified custom field """
                custom_value = _builder.values_model_class.objects.get_or_create(custom_field__name=field_name,
                                                                                 object_id=self.pk)[0]
                custom_value.value = value
                # TODO - must perform a full_clean here ?
                # custom_value.full_clean()
                custom_value.save()
                return custom_value

        return CustomModelMixin
