from django.db import models

from custard.builder import CustomFieldsBuilder

#==============================================================================
builder = CustomFieldsBuilder('tests.CustomFieldsModel',
                              'tests.CustomValuesModel')
CustomMixinClass = builder.create_mixin()
CustomManagerClass = builder.create_manager()

class SimpleModelWithoutManager(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name

class SimpleModelWithManager(models.Model, CustomMixinClass):
    name = models.CharField(max_length=255)

    objects = CustomManagerClass()

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name

class CustomFieldsModel(builder.create_fields()):
    class Meta:
        app_label = 'tests'

class CustomValuesModel(builder.create_values()):
    class Meta:
        app_label = 'tests'

#==============================================================================
builder_unique = CustomFieldsBuilder('tests.CustomFieldsUniqueModel',
                                     'tests.CustomValuesUniqueModel')

class SimpleModelUnique(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name

class CustomFieldsUniqueModel(builder_unique.create_fields()):
    def validate_unique(self, exclude=None):
        self._check_validate_already_defined_in_model()
        self._check_validate_already_defined_in_custom_fields()

    class Meta:
        app_label = 'tests'

class CustomValuesUniqueModel(builder_unique.create_values()):
    class Meta:
        app_label = 'tests'
