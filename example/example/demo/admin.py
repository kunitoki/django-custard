from django.contrib import admin

from custard.forms import CustomFieldModelBaseForm

from .models import Example, CustomFieldsModel, CustomValuesModel


class ExampleForm(CustomFieldModelBaseForm):

    def __init__(self, *args, **kwargs):
        super(ExampleForm, self).__init__(*args, **kwargs)
 
    def search_value_for_field(self, field, content_type, object_id):
        return CustomValuesModel.objects.filter(custom_field=field,
                                                content_type=content_type,
                                                object_id=object_id)

    def create_value_for_field(self, field, object_id, value):
        return CustomValuesModel(custom_field=field,
                                 object_id=object_id,
                                 value=value)

    def get_fields_for_content_type(self, content_type):
        return CustomFieldsModel.objects.filter(content_type=content_type)

    class Meta:
        model = Example


class ExampleAdmin(admin.ModelAdmin):
    form = ExampleForm
    search_fields = ('name',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(ExampleAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.search(search_term)
        return queryset, use_distinct

admin.site.register(Example, ExampleAdmin)


class CustomFieldsModelAdmin(admin.ModelAdmin):
    pass
admin.site.register(CustomFieldsModel, CustomFieldsModelAdmin)


class CustomValuesModelAdmin(admin.ModelAdmin):
    pass
admin.site.register(CustomValuesModel, CustomValuesModelAdmin)
