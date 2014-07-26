import django
#from django.conf import settings
#from django.core.urlresolvers import reverse
#from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings

from custard.conf import CUSTOM_TYPE_TEXT, settings
from custard.models import custom
from custard.forms import CustomFieldModelBaseForm

from .models import (SimpleModelWithManager, SimpleModelWithoutManager,
    CustomFieldsModel, CustomValuesModel)


#==============================================================================
class SimpleModelWithManagerForm(CustomFieldModelBaseForm):
    class Meta:
        model = SimpleModelWithManager

    def get_fields_for_content_type(self, content_type):
        return CustomFieldsModel.objects.filter(content_type=content_type)

    def search_value_for_field(self, field, content_type, object_id):
        return CustomValuesModel.objects.filter(custom_field=field,
                                                content_type=content_type,
                                                object_id=object_id)

    def create_value_for_field(self, field, object_id, value):
        return CustomValuesModel(custom_field=field,
                                 object_id=object_id,
                                 value=value)

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
                                                   label='Text field',
                                                   data_type=CUSTOM_TYPE_TEXT)
        self.cf.save()

        self.cf2 = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                    name='another_text_field',
                                                    label='Text field 2',
                                                    data_type=CUSTOM_TYPE_TEXT,
                                                    required=True,
                                                    searchable=False)
        self.cf2.save()

        self.obj = SimpleModelWithManager.objects.create(name='old test')
        self.obj.save()

    def tearDown(self):
        CustomFieldsModel.objects.all().delete()

    @override_settings(CUSTOM_CONTENT_TYPES=['simplemodelwithmanager'])
    def test_creation(self):
        class TestCustomFieldsModel(custom.create_fields()):
            class Meta:
                app_label = 'tests'

        self.assertQuerysetEqual(ContentType.objects.filter(TestCustomFieldsModel.CONTENT_TYPES),
                                 ContentType.objects.filter(Q(name__in=['simplemodelwithmanager'])))

    def test_get_formfield_for_field(self):
        with self.settings(CUSTOM_FIELD_TYPES={CUSTOM_TYPE_TEXT: 'django.forms.fields.TextField'}):
            form = SimpleModelWithManagerForm(data={}, instance=self.obj)
            self.assertIsNotNone(form.get_formfield_for_field(self.cf))
            self.assertEqual(django.forms.fields.TextField, form.get_formfield_for_field(self.cf).__class__)

    def test_get_widget_for_field(self):
        with self.settings(CUSTOM_WIDGET_TYPES={CUSTOM_TYPE_TEXT: 'django.forms.widgets.CheckboxInput'}):
            form = SimpleModelWithManagerForm(data={}, instance=self.obj)
            self.assertIsNotNone(form.get_widget_for_field(self.cf))
            self.assertEqual(django.forms.widgets.CheckboxInput, form.get_widget_for_field(self.cf).__class__)

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
