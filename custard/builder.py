from __future__ import unicode_literals
from django.db import models
from django.db.models import Q
from django import forms
from django.apps import apps
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .conf import (CUSTOM_TYPE_TEXT, CUSTOM_TYPE_INTEGER, CUSTOM_TYPE_FLOAT,
    CUSTOM_TYPE_TIME, CUSTOM_TYPE_DATE, CUSTOM_TYPE_DATETIME, CUSTOM_TYPE_BOOLEAN,
    settings)
from .utils import import_class


#==============================================================================
class CustomFieldsBuilder(object):
    """
    The builder class is the core of django-custard.
    From here it is possible to setup custom fields support for your models.
    """

    #--------------------------------------------------------------------------
    def __init__(self, fields_model, values_model,
                 custom_content_types=settings.CUSTOM_CONTENT_TYPES):
        """
        Custom fields builder class. This helps defining classes to enable
        custom fields in application.

        :param fields_model: the app.Model name of fields model
        :param values_model: the app.Model name of the values model
        :param custom_content_types: which content types are allowed to have custom fields
        :return:
        """
        self.fields_model = fields_model.split(".")
        self.values_model = values_model.split(".")
        self.custom_content_types = custom_content_types
        if self.custom_content_types and len(self.custom_content_types):
            self.content_types_query = None
            for c in self.custom_content_types:
                model_tuple = c.split(".")
                model_query = Q(app_label=model_tuple[0], model=model_tuple[1])
                if self.content_types_query:
                    self.content_types_query |= model_query
                else:
                    self.content_types_query = model_query
        else:
            self.content_types_query = Q()

    #--------------------------------------------------------------------------
    @property
    def fields_model_class(self):
        return apps.get_model(self.fields_model[0], self.fields_model[1])

    @property
    def values_model_class(self):
        return apps.get_model(self.values_model[0], self.values_model[1])

    #--------------------------------------------------------------------------
    def create_fields(self, base_model=models.Model, base_manager=models.Manager):
        """
        This method will create a model which will hold field types defined
        at runtime for each ContentType.

        :param base_model: base model class to inherit from
        :return:
        """

        CONTENT_TYPES = self.content_types_query

        class CustomContentTypeFieldManager(base_manager):
            pass

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
                                             verbose_name=_('content type'),
                                             related_name='+',
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

            objects = CustomContentTypeFieldManager()

            class Meta:
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

            def _check_validate_already_defined_in_model(self):
                model = self.content_type.model_class()
                if self.name in [f.name for f in model._meta.fields]:
                    raise ValidationError({ 'name': (_('Custom field already defined as model field for content type %(model_name)s') % {'model_name': model.__name__},) })

            def _check_validate_already_defined_in_custom_fields(self):
                model = self.content_type.model_class()
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

    #--------------------------------------------------------------------------
    def create_values(self, base_model=models.Model, base_manager=models.Manager):
        """
        This method will create a model which will hold field values for
        field types of custom_field_model.

        :param base_model:
        :param base_manager:
        :return:
        """

        _builder = self

        class CustomContentTypeFieldValueManager(base_manager):
            def create(self, **kwargs):
                """
                Subclass create in order to be able to use "value" in kwargs
                instead of using "value_%s" passing also type directly
                """
                if 'value' in kwargs:
                    value = kwargs.pop('value')
                    created_object = super(CustomContentTypeFieldValueManager, self).create(**kwargs)
                    created_object.value = value
                    return created_object
                else:
                    return super(CustomContentTypeFieldValueManager, self).create(**kwargs)

        @python_2_unicode_compatible
        class CustomContentTypeFieldValue(base_model):
            custom_field = models.ForeignKey('.'.join(_builder.fields_model),
                                             verbose_name=_('custom field'),
                                             related_name='+')
            content_type = models.ForeignKey(ContentType, editable=False,
                                             verbose_name=_('content type'),
                                             limit_choices_to=_builder.content_types_query)
            object_id = models.PositiveIntegerField(_('object id'), db_index=True)
            content_object = GenericForeignKey('content_type', 'object_id')

            value_text = models.TextField(blank=True, null=True)
            value_integer = models.IntegerField(blank=True, null=True)
            value_float = models.FloatField(blank=True, null=True)
            value_time = models.TimeField(blank=True, null=True)
            value_date = models.DateField(blank=True, null=True)
            value_datetime = models.DateTimeField(blank=True, null=True)
            value_boolean = models.NullBooleanField(blank=True)

            objects = CustomContentTypeFieldValueManager()

            def _get_value(self):
                return getattr(self, 'value_%s' % self.custom_field.data_type)

            def _set_value(self, new_value):
                setattr(self, 'value_%s' % self.custom_field.data_type, new_value)

            value = property(_get_value, _set_value)

            class Meta:
                unique_together = ('custom_field', 'content_type', 'object_id')
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
                return "%s: %s" % (self.custom_field.name, self.value)

        return CustomContentTypeFieldValue

    #--------------------------------------------------------------------------
    def create_manager(self, base_manager=models.Manager):
        """
        This will create the custom Manager that will use the fields_model and values_model
        respectively.

        :param base_manager: the base manager class to inherit from
        :return:
        """

        _builder = self

        class CustomManager(base_manager):
            def search(self, search_data, custom_args={}):
                """
                Search inside the custom fields for this model for any match
                 of search_data and returns existing model instances

                :param search_data:
                :param custom_args:
                :return:
                """
                query = None
                lookups = (
                    '%s__%s' % ('value_text', 'icontains'),
                )
                content_type = ContentType.objects.get_for_model(self.model)
                custom_args = dict({ 'content_type': content_type, 'searchable': True }, **custom_args)
                custom_fields = dict((f.name, f) for f in _builder.fields_model_class.objects.filter(**custom_args))
                for value_lookup in lookups:
                    for key, f in custom_fields.items():
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

    #--------------------------------------------------------------------------
    def create_mixin(self):
        """
        This will create the custom Model Mixin to attach to your custom field
        enabled model.

        :return:
        """

        _builder = self

        class CustomModelMixin(object):
            @cached_property
            def _content_type(self):
                return ContentType.objects.get_for_model(self)

            @classmethod
            def get_model_custom_fields(cls):
                """ Return a list of custom fields for this model, callable at model level """
                return _builder.fields_model_class.objects.filter(content_type=ContentType.objects.get_for_model(cls))

            def get_custom_fields(self):
                """ Return a list of custom fields for this model """
                return _builder.fields_model_class.objects.filter(content_type=self._content_type)

            def get_custom_value(self, field):
                """ Get a value for a specified custom field """
                return _builder.values_model_class.objects.get(custom_field=field,
                                                               content_type=self._content_type,
                                                               object_id=self.pk)

            def set_custom_value(self, field, value):
                """ Set a value for a specified custom field """
                custom_value, created = \
                    _builder.values_model_class.objects.get_or_create(custom_field=field,
                                                                      content_type=self._content_type,
                                                                      object_id=self.pk)
                custom_value.value = value
                custom_value.full_clean()
                custom_value.save()
                return custom_value

            #def __getattr__(self, name):
            #    """ Get a value for a specified custom field """
            #    try:
            #        obj = _builder.values_model_class.objects.get(custom_field__name=name,
            #                                                      content_type=self._content_type,
            #                                                      object_id=self.pk)
            #        return obj.value
            #    except ObjectDoesNotExist:
            #        pass
            #    return super(CustomModelMixin, self).__getattr__(name)

        return CustomModelMixin

    #--------------------------------------------------------------------------
    def create_modelform(self, base_form=forms.ModelForm,
                         field_types=settings.CUSTOM_FIELD_TYPES,
                         widget_types=settings.CUSTOM_WIDGET_TYPES):
        """
        This creates the class that implements a ModelForm that knows about
        the custom fields

        :param base_form:
        :param field_types:
        :param widget_types:
        :return:
        """

        _builder = self

        class CustomFieldModelBaseForm(base_form):
            def __init__(self, *args, **kwargs):
                """
                Constructor
                """
                # additional form variables
                self.custom_classes = None
                self.is_custom_form = True
                self.instance = None

                # construct the form
                super(CustomFieldModelBaseForm, self).__init__(*args, **kwargs)

                # init custom fields from model in the form
                self.init_custom_fields()

            def clean(self):
                """
                Clean the form
                """
                cleaned_data = super(CustomFieldModelBaseForm, self).clean()
                return cleaned_data

            def save(self, commit=True):
                """
                Save the form
                """
                self.instance = super(CustomFieldModelBaseForm, self).save(commit=commit)
                if self.instance and commit:
                    self.instance.save()
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
                    self.fields[name].label = f.label
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
                """ Perform save and validation over the custom fields """
                if not self.instance.pk:
                    raise Exception("The model instance has not been saved. Have you called instance.save() ?")

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
                field_type = import_class(field_types[field.data_type])
                return field_type(**field_attrs)

            def get_widget_for_field(self, field, attrs={}):
                """
                Returns the defined widget type instance built from the type of the field

                :param field: custom field instance
                :param attrs: attributes of widgets
                :return: the widget instance
                """
                return import_class(widget_types[field.data_type])(**attrs)

            def get_fields_for_content_type(self, content_type):
                """
                Returns all fields for a given content type

                Example implementation:

                  return MyCustomField.objects.filter(content_type=content_type)

                :param content_type: content type to search
                :return: the custom field instances
                """

                return _builder.fields_model_class.objects.filter(content_type=content_type)

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
                return _builder.values_model_class.objects.filter(custom_field=field,
                                                                  content_type=content_type,
                                                                  object_id=object_id)

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
                return _builder.values_model_class(custom_field=field,
                                                   object_id=object_id,
                                                   value=value)

        return CustomFieldModelBaseForm


    def create_modeladmin(self, base_admin=admin.ModelAdmin):
        """
        This creates the class that implements a ModelForm that knows about
        the custom fields

        :param base_admin:
        :return:
        """

        _builder = self

        class CustomFieldModelBaseAdmin(base_admin):
            def __init__(self, *args, **kwargs):
                super(CustomFieldModelBaseAdmin, self).__init__(*args, **kwargs)

            def save_model(self, request, obj, form, change):
                obj.save()
                if hasattr(form, 'save_custom_fields'):
                    form.save_custom_fields()

        return CustomFieldModelBaseAdmin


#===============================================================================
# This class is an empty class to avoid migrations errors
class CustomModelMixin(object):
    pass
