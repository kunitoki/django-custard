from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from custard.conf import *
from custard.models import custom, AlreadyRegistered, NotRegistered

from .models import *


class CustomModelsTestCase(TestCase):
        
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_registry(self):
        with self.settings(CUSTOM_CONTENT_TYPES={'simplemodelwithmanager', 'simplemodelwithoutmanager'}):
            pass

    def test_creation(self):
        cf = CustomFieldsModel.objects.create(content_type=ContentType.objects.get_for_model(SimpleModelWithManager),
                                              name='text_field',
                                              label='Text field',
                                              data_type=CUSTOM_TYPE_TEXT)
        cf.save()
        
