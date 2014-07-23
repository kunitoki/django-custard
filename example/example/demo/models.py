from django.db import models

from custard.models import custom

# Create your models here.

CustomModelMixin = custom.create_mixin('demo.CustomFieldsModel', 'demo.CustomValuesModel')
CustomModelManager = custom.create_manager('demo.CustomFieldsModel', 'demo.CustomValuesModel')


class Example(models.Model, CustomModelMixin):
    name = models.CharField(max_length=255)

    objects = CustomModelManager()
    
    def __str__(self):
        return "%s" % self.name


class CustomFieldsModel(custom.create_fields()):
    class Meta:
        verbose_name = 'custom field'
        verbose_name_plural = 'custom fields'


class CustomValuesModel(custom.create_values(CustomFieldsModel)):
    class Meta:
        verbose_name = 'custom field value'
        verbose_name_plural = 'custom field values'
