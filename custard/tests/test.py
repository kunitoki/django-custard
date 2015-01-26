from __future__ import unicode_literals
import django
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.test.utils import override_settings

from custard.conf import (CUSTOM_TYPE_TEXT, CUSTOM_TYPE_INTEGER,
                          CUSTOM_TYPE_BOOLEAN, CUSTOM_TYPE_FLOAT,
                          CUSTOM_TYPE_DATE, CUSTOM_TYPE_DATETIME,
                          CUSTOM_TYPE_TIME, settings)
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
        self.factory = RequestFactory()

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
        self.cf2.clean()
        self.cf2.save()

        self.cf3 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='int_field', label="Integer field",
                                                    data_type=CUSTOM_TYPE_INTEGER)
        self.cf3.save()

        self.cf4 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='boolean_field', label="Boolean field",
                                                    data_type=CUSTOM_TYPE_BOOLEAN)
        self.cf4.save()

        self.cf5 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='float_field', label="Float field",
                                                    data_type=CUSTOM_TYPE_FLOAT)
        self.cf5.save()

        self.cf6 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='date_field', label="Date field",
                                                    data_type=CUSTOM_TYPE_DATE)
        self.cf6.save()

        self.cf7 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='datetime_field', label="Datetime field",
                                                    data_type=CUSTOM_TYPE_DATETIME)
        self.cf7.save()

        self.cf8 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='time_field', label="Time field",
                                                    data_type=CUSTOM_TYPE_TIME)
        self.cf8.save()

        self.obj = SimpleModelWithManager.objects.create(name='old test')
        self.obj.save()

    def tearDown(self):
        CustomFieldsModel.objects.all().delete()

    def test_import_class(self):
        self.assertEqual(import_class('custard.builder.CustomFieldsBuilder'), CustomFieldsBuilder)

    def test_model_repr(self):
        self.assertEqual(repr(self.cf), "<CustomFieldsModel: text_field>")

        val = CustomValuesModel.objects.create(custom_field=self.cf,
                                               object_id=self.obj.pk,
                                               value="abcdefg")
        val.save()
        self.assertEqual(repr(val), "<CustomValuesModel: text_field: abcdefg>")

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

        val = CustomValuesModel.objects.create(custom_field=self.cf,
                                               object_id=self.obj.pk,
                                               value="123456")
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
                                               object_id=self.obj.pk,
                                               value="qwertyuiop")
        val.save()
        self.assertEqual(val.content_type, self.simple_with_manager_ct)
        self.assertEqual(val.content_type, val.custom_field.content_type)
        self.assertEqual(val.value_text, "qwertyuiop")
        self.assertEqual(val.value, "qwertyuiop")

    def test_value_search(self):
        newobj = SimpleModelWithManager.objects.create(name='new simple')
        newobj.save()

        v1 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=self.obj.pk,
                                              value="qwertyuiop")
        v1.save()

        v2 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=newobj.pk,
                                              value="qwertyuiop")
        v2.save()

        v3 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=newobj.pk,
                                              value="000asdf123")
        v3.save()

        qs1 = SimpleModelWithManager.objects.search("asdf")
        self.assertQuerysetEqual(qs1, [repr(newobj)])

        qs2 = SimpleModelWithManager.objects.search("qwerty")
        self.assertQuerysetEqual(qs2, [repr(self.obj), repr(newobj)], ordered=False)

    def test_value_search_not_searchable_field(self):
        v1 = CustomValuesModel.objects.create(custom_field=self.cf,
                                              object_id=self.obj.pk,
                                              value="12345")
        v1.save()

        v2 = CustomValuesModel.objects.create(custom_field=self.cf2,
                                              object_id=self.obj.pk,
                                              value="67890")
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
                    fields = '__all__'
                    model = SimpleModelWithManager

            form = SimpleModelWithManagerForm2(data={}, instance=self.obj)
            self.assertIsNotNone(form.get_widget_for_field(self.cf))
            self.assertEqual(django.forms.widgets.CheckboxInput, form.get_widget_for_field(self.cf).__class__)

    def test_form(self):
        class TestForm(builder.create_modelform()):
            custom_name = 'My Custom Fields'
            custom_description = 'Edit the Example custom fields here'
            custom_classes = 'zzzap-class'
            class Meta:
                fields = '__all__'
                model = SimpleModelWithManager

        request = self.factory.post('/', { 'text_field': '123' })
        form = TestForm(request.POST, instance=self.obj)
        self.assertFalse(form.is_valid())
        self.assertIn('another_text_field', form.errors)
        self.assertRaises(ValueError, lambda: form.save())

        request = self.factory.post('/', { 'id': self.obj.pk,
                                           'name': 'xxx',
                                           'another_text_field': 'wwwzzzyyyxxx' })
        form = TestForm(request.POST, instance=self.obj)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.obj.get_custom_value('another_text_field'), 'wwwzzzyyyxxx')
        self.assertEqual(self.obj.name, 'xxx')

        #self.assertInHTML(TestForm.custom_name, form.as_p())
        #self.assertInHTML(TestForm.custom_description, form.as_p())
        #self.assertInHTML(TestForm.custom_classes, form.as_p())

    def test_admin(self):
        modeladmin_class = builder.create_modeladmin()
        #c = Client()
        #if c.login(username='fred', password='secret'):
        #    response = c.get('/admin/', follow=True)
        #    print(response)