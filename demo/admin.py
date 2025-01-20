# Register your models here.

from django.contrib import admin
from demo.models import Book

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
