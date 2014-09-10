import django
#from django.conf import settings
#from django.core.urlresolvers import reverse
#from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings

from custard.conf import CUSTOM_TYPE_TEXT, CUSTOM_TYPE_INTEGER, settings
from custard.builder import CustomFieldsBuilder
from custard.utils import import_class

from .models import (SimpleModelWithManager, SimpleModelWithoutManager,
    CustomFieldsModel, CustomValuesModel, builder)


#==============================================================================
class SimpleModelWithManagerForm(builder.create_modelform()):
    class Meta:
        model = SimpleModelWithManager
        fields = '__all__'

#class ExampleAdmin(admin.ModelAdmin):
#    form = ExampleForm
#    search_fields = ('name',)
#
#    def get_search_results(self, request, queryset, search_term):
#        queryset, use_distinct = super(ExampleAdmin, self).get_search_results(request, queryset, search_term)
#        queryset |= self.model.objects.search(search_term)
#        return queryset, use_distinct
#
# admin.site.register(Example, ExampleAdmin)

#==============================================================================
class CustomModelsTestCase(TestCase):
        
    def setUp(self):
        self.simple_with_manager_ct = ContentType.objects.get_for_model(SimpleModelWithManager)
        self.simple_without_manager_ct = ContentType.objects.get_for_model(SimpleModelWithoutManager)

        self.cf = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                   name='text_field',
                                                   label="Text field",
                                                   data_type=CUSTOM_TYPE_TEXT)
        self.cf.save()

        self.cf2 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='another_text_field',
                                                    label="Text field 2",
                                                    data_type=CUSTOM_TYPE_TEXT,
                                                    required=True,
                                                    searchable=False)
        self.cf2.save()

        self.obj = SimpleModelWithManager.objects.create(name='old test')
        self.obj.save()

    def tearDown(self):
        CustomFieldsModel.objects.all().delete()

    def test_import_class(self):
        self.assertEqual(import_class('custard.builder.CustomFieldsBuilder'), CustomFieldsBuilder)

    @override_settings(CUSTOM_CONTENT_TYPES=['simplemodelwithmanager'])
    def test_field_creation(self):
        builder2 = CustomFieldsBuilder('tests.CustomFieldsModel',
                                       'tests.CustomValuesModel',
                                       settings.CUSTOM_CONTENT_TYPES)

        class TestCustomFieldsModel(builder2.create_fields()):
            class Meta:
                app_label = 'tests'

        self.assertQuerysetEqual(ContentType.objects.filter(builder2.content_types_query),
                                 ContentType.objects.filter(Q(name__in=['simplemodelwithmanager'])))

    def test_mixin(self):
        self.assertIn(self.cf, self.obj.get_custom_fields())
        self.assertIn(self.cf, SimpleModelWithManager.get_model_custom_fields())
        self.assertEqual(self.cf, self.obj.get_custom_field('text_field'))

        val = CustomValuesModel.objects.create(custom_field=self.cf, object_id=self.obj.pk)
        val.value = "123456"
        val.save()
        self.assertEqual("123456", self.obj.get_custom_value('text_field'))

        self.obj.set_custom_value('text_field', "abcdefg")
        self.assertEqual("abcdefg", self.obj.get_custom_value('text_field'))

        val.delete()

    def test_field_model_clean(self):
        cf = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                              name='another_text_field',
                                              label="Text field already present",
                                              data_type=CUSTOM_TYPE_INTEGER)
        with self.assertRaises(ValidationError):
            cf.full_clean()

        cf = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                              name='name',
                                              label="Text field already in model",
                                              data_type=CUSTOM_TYPE_TEXT)
        with self.assertRaises(ValidationError):
            cf.full_clean()

    def test_value_model_clean(self):
        val = CustomValuesModel.objects.create(custom_field=self.cf2,
                                               object_id=self.obj.pk)
        val.value = "qwertyuiop"
        val.save()

        val = CustomValuesModel.objects.create(custom_field=self.cf2,
                                               object_id=self.obj.pk)
        val.value = "qwertyuiop"
        with self.assertRaises(ValidationError):
            val.full_clean()

    def test_value_creation(self):
        val = CustomValuesModel.objects.create(custom_field=self.cf,
                                               object_id=self.obj.pk)
        val.value = "qwertyuiop"
        val.save()
        self.assertEqual(val.content_type, self.simple_with_manager_ct)
        self.assertEqual(val.content_type, val.custom_field.content_type)
        self.assertEqual(val.value_text, "qwertyuiop")
        self.assertEqual(val.value, "qwertyuiop")

    def test_value_search(self):
        newobj = SimpleModelWithManager.objects.create(name='new simple')
        newobj.save()

        v1 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=self.obj.pk)
        v1.value = "qwertyuiop"
        v1.save()

        v2 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=newobj.pk)
        v2.value = "qwertyasdf"
        v2.save()

        qs1 = SimpleModelWithManager.objects.search("asdf")
        self.assertQuerysetEqual(qs1, [repr(newobj)])

        qs2 = SimpleModelWithManager.objects.search("qwerty")
        self.assertQuerysetEqual(qs2, [repr(self.obj), repr(newobj)], ordered=False)

    def test_value_search_not_searchable_field(self):
        v1 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=self.obj.pk)
        v1.value = "12345"
        v1.save()

        v2 = CustomValuesModel.objects.create(custom_field=self.cf2,
                                              object_id=self.obj.pk)
        v2.value = "67890"
        v2.save()

        qs1 = SimpleModelWithManager.objects.search("12345")
        self.assertQuerysetEqual(qs1, [repr(self.obj)])

        qs2 = SimpleModelWithManager.objects.search("67890")
        self.assertQuerysetEqual(qs2, [])

    def test_get_formfield_for_field(self):
        with self.settings(CUSTOM_FIELD_TYPES={CUSTOM_TYPE_TEXT: 'django.forms.fields.EmailField'}):
            builder2 = CustomFieldsBuilder('tests.CustomFieldsModel', 'tests.CustomValuesModel')

            class SimpleModelWithManagerForm2(builder2.create_modelform(field_types=settings.CUSTOM_FIELD_TYPES)):
                class Meta:
                    model = SimpleModelWithManager
                    fields = '__all__'

            form = SimpleModelWithManagerForm2(data={}, instance=self.obj)
            self.assertIsNotNone(form.get_formfield_for_field(self.cf))
            self.assertEqual(django.forms.fields.EmailField, form.get_formfield_for_field(self.cf).__class__)

    def test_get_widget_for_field(self):
        with self.settings(CUSTOM_WIDGET_TYPES={CUSTOM_TYPE_TEXT: 'django.forms.widgets.CheckboxInput'}):
            builder2 = CustomFieldsBuilder('tests.CustomFieldsModel', 'tests.CustomValuesModel')

            class SimpleModelWithManagerForm2(builder2.create_modelform(widget_types=settings.CUSTOM_WIDGET_TYPES)):
                class Meta:
                    model = SimpleModelWithManager

            form = SimpleModelWithManagerForm2(data={}, instance=self.obj)
            self.assertIsNotNone(form.get_widget_for_field(self.cf))
            self.assertEqual(django.forms.widgets.CheckboxInput, form.get_widget_for_field(self.cf).__class__)
