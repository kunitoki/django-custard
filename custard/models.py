import warnings
from django.db import models

#==============================================================================
class CustomContentType(object):

    def create_fields(self, base_model=models.Model):
        warnings.warn("The custard.models.custom singleton has been superseded by custard.builder.CustomFieldsBuilder")
        return base_model

    def create_values(self, custom_field_model, base_model=models.Model):
        warnings.warn("The custard.models.custom singleton has been superseded by custard.builder.CustomFieldsBuilder")
        return base_model

    def create_manager(self, fields_model, values_model, base_manager=models.Manager):
        warnings.warn("The custard.models.custom singleton has been superseded by custard.builder.CustomFieldsBuilder")
        return base_manager

    def create_mixin(self, fields_model, values_model):
        warnings.warn("The custard.models.custom singleton has been superseded by custard.builder.CustomFieldsBuilder")
        return object

#==============================================================================
custom = CustomContentType()
