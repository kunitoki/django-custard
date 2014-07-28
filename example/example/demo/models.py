from django.db import models

from custard.builder import CustomFieldsBuilder

# Create your models here.

builder = CustomFieldsBuilder('demo.CustomFieldsModel', 'demo.CustomValuesModel')
CustomMixinClass = builder.create_mixin()
CustomManagerClass = builder.create_manager()


class Example(models.Model, CustomMixinClass):
    name = models.CharField(max_length=255)

    objects = CustomManagerClass()

    def __str__(self):
        return "%s" % self.name


class CustomFieldsModel(builder.create_fields()):
    pass


class CustomValuesModel(builder.create_values()):
    pass
