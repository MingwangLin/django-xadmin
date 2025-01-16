from django.shortcuts import render
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.response import Response

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from common.core.pagination import DynamicPageNumber
from project_batch.models import ProjectBatch
from project_batch.serializers import ProjectBatchSerializer


class ProjectBatchViewSetFilter(BaseFilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category')
    classification = filters.CharFilter(field_name='classification')
    status = filters.CharFilter(field_name='status')
    project = filters.CharFilter(field_name='project')
    exam_begin_date = filters.DateFromToRangeFilter()
    exam_end_date = filters.DateFromToRangeFilter()

    class Meta:
        model = ProjectBatch
        fields = ['name', 'code', 'category', 'classification', 'status', 'project',
                 'exam_begin_date', 'exam_end_date', 'created_time']


class ProjectBatchViewSet(BaseModelSet, ImportExportDataAction):
    """项目批次管理"""
    queryset = ProjectBatch.objects.all()
    serializer_class = ProjectBatchSerializer
    ordering_fields = ['created_time']
    filterset_class = ProjectBatchViewSetFilter
    pagination_class = DynamicPageNumber(1000)

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    @action(methods=['POST'], detail=False)
    def query(self, request, *args, **kwargs):
        # Create a new QueryDict with request.data
        query_dict = request.query_params.copy()
        for key, value in request.data.items():
            if isinstance(value, list):
                query_dict.setlist(key, value)
            else:
                query_dict[key] = value
                
        request._request.GET = query_dict  # Set the underlying GET parameters
        return self.list(request, *args, **kwargs)
