from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Example, CustomFieldsModel, CustomValuesModel, builder


#==============================================================================
class ExampleForm(builder.create_modelform()):
    class Meta:
        model = Example
        fields = '__all__'


class ExampleAdmin(builder.create_modeladmin()):
    form = ExampleForm
    custom_search = True

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(ExampleAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.search(search_term)
        return queryset, use_distinct

admin.site.register(Example, ExampleAdmin)


#==============================================================================
class MyUserChangeForm(builder.create_modelform(base_form=UserChangeForm)):
    custom_name = 'Custom fields'
    custom_description = 'Custom fields editing'
    custom_classes = ''

    class Meta:
        model = User
        fields = '__all__'

class MyUserCreationForm(builder.create_modelform(base_form=UserCreationForm)):
    custom_name = 'Custom fields'
    custom_description = 'Custom fields editing'
    custom_classes = ''

    class Meta:
        model = User
        fields = '__all__'

class MyUserAdmin(builder.create_modeladmin(base_admin=UserAdmin)):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


#==============================================================================
class CustomFieldsModelInline(admin.TabularInline):
    model = CustomFieldsModel
    extra = 0

class ContentTypeModelAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'app_label', 'model',)
    inlines = [CustomFieldsModelInline]

    def get_queryset(self, request):
        qs = super(ContentTypeModelAdmin, self).get_queryset(request)
        return qs.filter(builder.content_types_query)

admin.site.register(ContentType, ContentTypeModelAdmin)


#==============================================================================
class CustomFieldsModelAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomFieldsModel, CustomFieldsModelAdmin)


class CustomValuesModelAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomValuesModel, CustomValuesModelAdmin)
