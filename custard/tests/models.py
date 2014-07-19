from django.db import models

from custard.models import custom


class SimpleModelNotRegistered(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "%s" % self.name


class SimpleModelWithoutManager(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name


class SimpleModelWithManager(models.Model):
    name = models.CharField(max_length=255)
    custom = custom.create_manager('tests.CustomFieldsModel', 'tests.CustomValuesModel')   

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return "%s" % self.name


class CustomFieldsModel(custom.create_fields()):
    class Meta:
        verbose_name = 'custom field'
        verbose_name_plural = 'custom fields'
        app_label = 'tests'

class CustomValuesModel(custom.create_values(CustomFieldsModel)):
    class Meta:
        verbose_name = 'custom field value'
        verbose_name_plural = 'custom field values'
        app_label = 'tests'
