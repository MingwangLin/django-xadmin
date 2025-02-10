from django.contrib import admin
from region.models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'full_name', 'type', 'status', 'is_capital', 'sort_order')
    list_filter = ('type', 'status', 'is_capital')
    search_fields = ('code', 'name', 'full_name')
    ordering = ('sort_order', 'created_time')
