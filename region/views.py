from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.plumbing import build_array_type, build_basic_type

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from common.core.pagination import DynamicPageNumber
from common.core.queryset_helper import QuerysetHelper
from common.core.response import ApiResponse
from region.models import Region
from region.serializers import RegionSerializer
from rest_framework.decorators import action


class RegionViewSetFilter(BaseFilterSet):
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    full_name = filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    type = filters.NumberFilter(field_name='type')
    status = filters.CharFilter(field_name='status')
    is_capital = filters.BooleanFilter(field_name='is_capital')

    class Meta:
        model = Region
        fields = ['code', 'name', 'full_name', 'type', 'status', 'is_capital', 'created_time']


class RegionViewSet(BaseModelSet, ImportExportDataAction):
    """Region Management"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    ordering_fields = ['sort_order', 'created_time']
    filterset_class = RegionViewSetFilter
    pagination_class = DynamicPageNumber(1000)

    def get_queryset(self):
        queryset = super().get_queryset()
        request_data = self.request.data

        if isinstance(request_data, dict):
            queryset = QuerysetHelper.apply_filter(queryset, request_data.get('filter'))
            queryset = QuerysetHelper.get_general_sort_keys_filtered_queryset(
                request_data.get('sortkeys'), queryset, queryset.model)
            queryset = QuerysetHelper.get_search_text_multiple_filtered_queryset(
                request_data, queryset, self.filterset_class.get_fields().keys())
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
        """查询区域"""
        return self.list(request, *args, **kwargs)