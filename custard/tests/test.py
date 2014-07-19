from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db.models.loading import load_app
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from .models import (SimpleModelWithoutManager, SimpleModelWithManager,
    CustomFieldsModel, CustomValuesModel)

from custard.conf import *
from custard.models import custom
   

class CustomModelsTestCase(TestCase):
    def _pre_setup(self):
        self.saved_INSTALLED_APPS = settings.INSTALLED_APPS
        self.saved_DEBUG = settings.DEBUG
        test_app = 'custard.tests'
        settings.INSTALLED_APPS = (list(self.saved_INSTALLED_APPS) + [test_app],)
        settings.DEBUG = True
        # load our fake application and syncdb
        load_app(test_app)
        call_command('syncdb', verbosity=0, interactive=False)
        super(CustomModelsTestCase, self)._pre_setup()

    def _post_teardown(self):
        settings.INSTALLED_APPS = self.saved_INSTALLED_APPS
        settings.DEBUG = self.saved_DEBUG
        super(CustomModelsTestCase, self)._post_teardown()

    def setUp(self):
        pass

    def test_registry(self):
        self.assertEqual(custom.registry.keys(), [SimpleModelWithoutManager, SimpleModelWithManager]) 
        self.assertEqual(custom.registry.values(), ['simplemodelwithoutmanager', 'simplemodelwithmanager']) 

    def test_creation(self):
        cf = CustomFieldsModel.objects.create(content_type=ContentType.get_for_model(SimpleModelWithManager),
                                              name='text_field',
                                              label='Text field',
                                              data_type=CUSTOM_TYPE_TEXT)
        cf.save()
