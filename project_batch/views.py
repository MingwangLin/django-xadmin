from django.shortcuts import render
from django_filters import rest_framework as filters
from drf_spectacular.plumbing import build_array_type, build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.response import Response

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from common.core.pagination import DynamicPageNumber
from common.core.queryset_helper import QuerysetHelper
from project_batch.models import ProjectBatch
from project_batch.serializers import ProjectBatchSerializer


class ProjectBatchViewSetFilter(BaseFilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category')
    classification = filters.CharFilter(field_name='classification')
    status = filters.CharFilter(field_name='status')
    project = filters.CharFilter(field_name='project')
    exam_type = filters.NumberFilter(field_name='exam_type')
    exam_begin_date = filters.DateFromToRangeFilter()
    exam_end_date = filters.DateFromToRangeFilter()
    schedule_count = filters.NumberFilter()
    total_exam_rooms = filters.NumberFilter()
    online_exam_rooms = filters.NumberFilter()
    stream_start_time = filters.DateTimeFromToRangeFilter()
    stream_end_time = filters.DateTimeFromToRangeFilter()
    enable_ai_monitoring = filters.BooleanFilter()
    show_ata_watermark = filters.BooleanFilter()
    video_display_text = filters.CharFilter(lookup_expr='icontains')
    videos_per_room = filters.NumberFilter()

    class Meta:
        model = ProjectBatch
        fields = ['name', 'code', 'category', 'classification', 'status', 'project',
                 'exam_type', 'exam_begin_date', 'exam_end_date', 'created_time', 'schedule_count',
                 'total_exam_rooms', 'online_exam_rooms', 'stream_start_time', 'stream_end_time',
                 'enable_ai_monitoring', 'show_ata_watermark', 'video_display_text', 'videos_per_room']


class ProjectBatchViewSet(BaseModelSet, ImportExportDataAction):
    """项目批次管理"""
    queryset = ProjectBatch.objects.all()
    serializer_class = ProjectBatchSerializer
    ordering_fields = ['created_time']
    filterset_class = ProjectBatchViewSetFilter
    pagination_class = DynamicPageNumber(1000)

    def get_queryset(self):
        queryset = super().get_queryset()
        request_data = self.request.data or {}
        queryset = QuerysetHelper.apply_filter(queryset, request_data.get('filter'))
        queryset = QuerysetHelper.get_general_sort_keys_filtered_queryset(request_data.get('sortkeys'), queryset,
                                                                          queryset.model)
        queryset = QuerysetHelper.get_search_text_multiple_filtered_queryset(request_data, queryset,
                                                                             self.filterset_class.get_fields().keys())
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='filter',
                type=OpenApiTypes.OBJECT,
                description='Complex filter object with format: {"rel": "and|or", "cond": [{"field": "field_name", "method": "exact|contains|in|etc", "value": "value", "type": "text|datetime|etc"}]}',
                required=False
            ),
            OpenApiParameter(
                name='sortkeys',
                type=build_array_type(build_basic_type(OpenApiTypes.STR)),
                description='List of fields to sort by. Prefix with "-" for descending order. Example: ["-created_time", "name"]',
                required=False
            ),
            OpenApiParameter(
                name='searchtext',
                type=OpenApiTypes.STR,
                description='Text to search across multiple fields defined in filter_fields',
                required=False
            ),
        ]
    )
    @action(methods=['POST'], detail=False)
    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
