# Register your models here.

from django.contrib import admin
from demo.models import Book, Receiving, ReceivingItem

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'isbn', 'category', 'author', 'publisher', 'price', 'is_active', 'publication_date']
    list_filter = ['category', 'is_active', 'publisher']
    search_fields = ['name', 'isbn', 'author', 'publisher']
    date_hierarchy = 'publication_date'
    filter_horizontal = ['managers', 'managers2']
    raw_id_fields = ['admin', 'admin2']
    readonly_fields = ['created_time', 'updated_time']
    fieldsets = [
        (None, {
            'fields': ['name', 'isbn', 'category', 'author', 'publisher', 'price', 'is_active']
        }),
        ('Dates', {
            'fields': ['publication_date', 'created_time', 'updated_time']
        }),
        ('Administrators', {
            'fields': ['admin', 'admin2', 'managers', 'managers2']
        }),
        ('Files', {
            'fields': ['cover', 'avatar', 'book_file']
        }),
    ]

@admin.register(Receiving)
class ReceivingAdmin(admin.ModelAdmin):
    list_display = ['type', 'status', 'receiving_warehouse_name', 'receiving_warehouse_code', 'confirm_time', 'external_code']
    list_filter = ['type', 'status']
    search_fields = ['receiving_warehouse_name', 'receiving_warehouse_code', 'external_code']
    date_hierarchy = 'confirm_time'
    readonly_fields = ['created_time', 'updated_time']
    fieldsets = [
        (None, {
            'fields': ['type', 'status', 'receiving_warehouse_name', 'receiving_warehouse_code', 'external_code']
        }),
        ('Dates', {
            'fields': ['confirm_time', 'created_time', 'updated_time']
        }),
    ]

@admin.register(ReceivingItem)
class ReceivingItemAdmin(admin.ModelAdmin):
    list_display = ['receiving', 'arrival_quantity', 'defect_quantity', 'external_key']
    list_filter = ['receiving__type', 'receiving__status']
    search_fields = ['receiving__receiving_warehouse_name', 'external_key']
    raw_id_fields = ['receiving']
    readonly_fields = ['created_time', 'updated_time']
    fieldsets = [
        (None, {
            'fields': ['receiving', 'arrival_quantity', 'defect_quantity', 'external_key']
        }),
        ('Dates', {
            'fields': ['created_time', 'updated_time']
        }),
    ]
