from rest_framework import serializers

from common.core.serializers import BaseModelSerializer
from project_batch import models


class ProjectBatchSerializer(BaseModelSerializer):
    class Meta:
        model = models.ProjectBatch
        fields = [
            'pk', 'name', 'code', 'ets_code', 'short_name', 'exam_type',
            'category', 'classification', 'exam_type_desc', 'exam_system_type_desc',
            'scene_type_desc', 'scene_type', 'invigilator_type', 'exam_begin_date',
            'exam_end_date', 'confirm_begin_date', 'confirm_end_date', 'status',
            'demands', 'tags', 'sync_timestamp', 'sync_allowed', 'sync_time',
            'remote_configs', 'manager', 'project_name', 'project_code',
            'start_department', 'department', 'project_department',
            'schedule_count', 'total_exam_rooms', 'online_exam_rooms',
            'created_time', 'updated_time'
        ]
        table_fields = [
            'pk', 'name', 'code', 'category', 'classification', 'status',
            'exam_begin_date', 'exam_end_date', 'schedule_count', 'total_exam_rooms',
            'online_exam_rooms', 'created_time'
        ]
        extra_kwargs = {
            'pk': {'read_only': True}
        } 