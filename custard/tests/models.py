from django.db import models

from custard.models import custom

CustomMixin = custom.create_mixin('tests.CustomFieldsModel', 'tests.CustomValuesModel')
CustomManager = custom.create_manager('tests.CustomFieldsModel', 'tests.CustomValuesModel')

class SimpleModelNotRegistered(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name


class SimpleModelWithoutManager(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name


class SimpleModelWithManager(models.Model, CustomMixin):
    name = models.CharField(max_length=255)

    objects = CustomManager()

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name


class CustomFieldsModel(custom.create_fields()):
    class Meta:
        app_label = 'tests'

class CustomValuesModel(custom.create_values(CustomFieldsModel)):
    class Meta:
        app_label = 'tests'
