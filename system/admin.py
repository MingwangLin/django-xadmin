# Register your models here.
from django.contrib import admin

# Register your models here.
from system.models import *

admin.site.register(UserInfo)
admin.site.register(DeptInfo)

class ModelLabelFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'field_type', 'parent')
    list_filter = ('field_type',)
    search_fields = ('name', 'label')
    raw_id_fields = ('parent',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

    class ModelLabelFieldExtensionInline(admin.StackedInline):
        model = ModelLabelFieldExtension
        can_delete = False
        max_num = 1
        min_num = 1

    inlines = [ModelLabelFieldExtensionInline]

admin.site.register(ModelLabelField, ModelLabelFieldAdmin)

admin.site.register(UserLoginLog)
admin.site.register(OperationLog)
admin.site.register(MenuMeta)
admin.site.register(Menu)
admin.site.register(DataPermission)
admin.site.register(FieldPermission)
admin.site.register(UserRole)
admin.site.register(UploadFile)
admin.site.register(SystemConfig)
admin.site.register(UserPersonalConfig)
admin.site.register(ModelSeparationField)
