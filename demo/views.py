# Create your views here.


from django_filters import rest_framework as filters
from rest_framework.decorators import action
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction, SearchColumnsAction
from common.core.pagination import DynamicPageNumber
from common.core.response import ApiResponse
from common.utils import get_logger
from demo.models import Book, Receiving, ReceivingItem
from demo.serializers.book import BookSerializer
from demo.serializers.book import ReceivingSerializer, ReceivingItemSerializer
from common.core.queryset_helper import QuerysetHelper
from drf_spectacular.plumbing import build_array_type, build_basic_type

logger = get_logger(__name__)


class BookViewSetFilter(BaseFilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author', lookup_expr='icontains')
    publisher = filters.CharFilter(field_name='publisher', lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['name', 'isbn', 'author', 'publisher', 'is_active', 'publication_date', 'price',
                  'created_time']  # fields用于前端自动生成的搜索表单


class BookViewSet(BaseModelSet, ImportExportDataAction):
    """书籍"""  # 这个 书籍 的注释得写， 否则菜单中可能会显示null，访问日志记录中也可能显示异常

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    ordering_fields = ['created_time']
    filterset_class = BookViewSetFilter
    pagination_class = DynamicPageNumber(1000)  # 表示最大分页数据1000条，如果注释，则默认最大100条数据

    @action(methods=['post'], detail=True)
    def push(self, request, *args, **kwargs):
        """推送到其他服务"""  # 这个 推送到其他服务 的注释得写， 否则菜单中可能会显示null，访问日志记录中也可能显示异常

        # 自定义一个请求为post的 push 路由行为，执行自定义操作， action装饰器有好多参数，可以查看源码自行分析
        instance = self.get_object()
        return ApiResponse(detail=f"{instance.name} 推送成功")


class ReceivingSearchColumnsMixin(SearchColumnsAction):
    """Custom mixin to add subitems to search-columns response for Receiving"""
    
    def get_subitems_info(self):
        """Get subitems info from ReceivingItemViewSet"""
        # Create a new instance of ReceivingItemViewSet with proper initialization
        receiving_item_view = ReceivingItemViewSet()
        receiving_item_view.request = self.request
        receiving_item_view.format_kwarg = self.format_kwarg
        receiving_item_view.action = 'search_columns'  # Set the action
        receiving_item_view.kwargs = {}  # Initialize kwargs
        receiving_item_view.args = ()    # Initialize args
        
        # Get search-columns data from ReceivingItemViewSet
        response = receiving_item_view.search_columns(self.request)
        return response.data.get('data', [])

    @action(methods=['get'], detail=False, url_path='search-columns')
    def search_columns(self, request, *args, **kwargs):
        """Override search-columns to include subitems"""
        # Get original response from parent class
        response = super().search_columns(request, *args, **kwargs)
        
        # Find the items field and add subitems
        for field in response.data['data']:
            if field['key'] == 'items':
                field['subitems'] = self.get_subitems_info()
                break
        
        return response


class ReceivingViewSetFilter(BaseFilterSet):
    receiving_warehouse_name = filters.CharFilter(field_name='receiving_warehouse_name', lookup_expr='icontains')
    receiving_warehouse_code = filters.CharFilter(field_name='receiving_warehouse_code', lookup_expr='icontains')
    external_code = filters.CharFilter(field_name='external_code', lookup_expr='icontains')

    class Meta:
        model = Receiving
        fields = ['receiving_warehouse_name', 'receiving_warehouse_code', 'external_code', 
                 'status', 'type', 'created_time']


class ReceivingViewSet(ReceivingSearchColumnsMixin, BaseModelSet):
    """入库管理"""

    queryset = Receiving.objects.all()
    serializer_class = ReceivingSerializer
    ordering_fields = ['created_time']
    filterset_class = ReceivingViewSetFilter
    pagination_class = DynamicPageNumber(1000)

    def get_queryset(self):
        queryset = super().get_queryset()
        request_data = self.request.data

        if type(request_data) == dict:
            queryset = QuerysetHelper.apply_filter(queryset, request_data.get('filter'))
            queryset = QuerysetHelper.get_general_sort_keys_filtered_queryset(request_data.get('sortkeys'), queryset, queryset.model)
            queryset = QuerysetHelper.get_search_text_multiple_filtered_queryset(request_data, queryset, self.filterset_class.get_fields().keys())
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

    @action(methods=['post'], detail=True)
    def confirm(self, request, *args, **kwargs):
        """确认入库"""
        instance = self.get_object()
        if instance.status == instance.StatusChoices.CONFIRMED:
            return ApiResponse(code=400, message="该入库单已确认")
        
        instance.status = instance.StatusChoices.CONFIRMED
        instance.confirm_time = timezone.now()
        instance.save(update_fields=['status', 'confirm_time'])
        return ApiResponse(detail=f"{instance.receiving_warehouse_name} 入库确认成功")


class ReceivingItemViewSet(BaseModelSet):
    """入库明细"""

    queryset = ReceivingItem.objects.all()
    serializer_class = ReceivingItemSerializer
    ordering_fields = ['created_time']
    pagination_class = DynamicPageNumber(1000)

    def get_queryset(self):
        queryset = super().get_queryset()
        receiving_id = self.request.query_params.get('receiving_id')
        if receiving_id:
            queryset = queryset.filter(receiving_id=receiving_id)
        return queryset
