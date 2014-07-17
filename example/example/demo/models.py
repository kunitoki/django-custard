from django.db import models

from custard.models import CustomContentType

# Create your models here.

class Example(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return "%s" % self.name
    
VALID_CUSTOM_CONTENT_TYPES = {
    'name__in': ['example',],
}

class CustomFieldsModel(CustomContentType.create_fields(VALID_CUSTOM_CONTENT_TYPES)):
    class Meta:
        verbose_name = 'custom field'
        verbose_name_plural = 'custom fields'

class CustomValuesModel(CustomContentType.create_values(CustomFieldsModel)):
    class Meta:
        verbose_name = 'custom field value'
        verbose_name_plural = 'custom field values'



