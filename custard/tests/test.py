import django
#from django.conf import settings
#from django.core.urlresolvers import reverse
#from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from custard.conf import CUSTOM_TYPE_TEXT
#from custard.models import custom, AlreadyRegistered, NotRegistered

from .models import (SimpleModelWithManager, SimpleModelWithoutManager,
    CustomFieldsModel, CustomValuesModel)


class CustomModelsTestCase(TestCase):
        
    def setUp(self):
        self.simple_with_manager_ct = ContentType.objects.get_for_model(SimpleModelWithManager)
        self.simple_without_manager_ct = ContentType.objects.get_for_model(SimpleModelWithoutManager)

        self.cf = CustomFieldsModel.objects.create(content_type=self.simple_with_manager_ct,
                                                   name='text_field',
                                                   label='Text field',
                                                   data_type=CUSTOM_TYPE_TEXT)
        self.cf.save()

    def tearDown(self):
        CustomFieldsModel.objects.all().delete()

    #def test_registry(self):
    #    with self.settings(CUSTOM_CONTENT_TYPES=['simplemodelwithmanager', 'simplemodelwithoutmanager']):
    #        self.assertIn('simplemodelwithmanager', CustomFieldsModel.DATATYPE_CHOICES.values())
    #        self.assertIn('simplemodelwithoutmanager', CustomFieldsModel.DATATYPE_CHOICES.values())
    #        self.assertNotIn('simplemodelnotregistered', CustomFieldsModel.DATATYPE_CHOICES.values())

    def test_creation(self):
        pass

    def test_get_form_fields(self):
        with self.settings(CUSTOM_FIELD_TYPES={CUSTOM_TYPE_TEXT: 'django.forms.fields.CharField'}):
            self.assertIsNotNone(self.cf.get_form_field())
            self.assertEqual(django.forms.fields.CharField, self.cf.get_form_field().__class__)
