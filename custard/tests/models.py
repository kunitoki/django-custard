from django.db import models

from custard.models import custom

class SimpleModelWithoutManager(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return "%s" % self.name

class SimpleModelWithManager(models.Model):
    name = models.CharField(max_length=255)
    
    custom = custom.create_manager('demo.CustomFieldsModel', 'demo.CustomValuesModel')   
    
    def __str__(self):
        return "%s" % self.name

custom.register(SimpleModelWithoutManager)
custom.register(SimpleModelWithManager)


class CustomFieldsModel(custom.create_fields()):
    class Meta:
        verbose_name = 'custom field'
        verbose_name_plural = 'custom fields'

class CustomValuesModel(custom.create_values(CustomFieldsModel)):
    class Meta:
        verbose_name = 'custom field value'
        verbose_name_plural = 'custom field values'
