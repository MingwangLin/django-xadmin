from django.contrib import admin
from project_batch import models


@admin.register(models.ProjectBatch)
class ProjectBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'classification', 'status', 'exam_begin_date', 'created_time')
    search_fields = ('name', 'code')
    list_filter = ('category', 'classification', 'status')
    ordering = ('-created_time',)
