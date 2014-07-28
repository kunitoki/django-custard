from django.contrib import admin

from .models import Example, CustomFieldsModel, CustomValuesModel, builder


class ExampleForm(builder.create_modelform()):
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
