# Create your views here.


from django_filters import rest_framework as filters
from rest_framework.decorators import action
from django.utils import timezone

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from common.core.pagination import DynamicPageNumber
from common.core.response import ApiResponse
from common.utils import get_logger
from demo.models import Book, Receiving, ReceivingItem
from demo.serializers.book import BookSerializer
from demo.serializers.book import ReceivingSerializer, ReceivingItemSerializer

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


class ReceivingViewSetFilter(BaseFilterSet):
    receiving_warehouse_name = filters.CharFilter(field_name='receiving_warehouse_name', lookup_expr='icontains')
    receiving_warehouse_code = filters.CharFilter(field_name='receiving_warehouse_code', lookup_expr='icontains')
    external_code = filters.CharFilter(field_name='external_code', lookup_expr='icontains')

    class Meta:
        model = Receiving
        fields = ['receiving_warehouse_name', 'receiving_warehouse_code', 'external_code', 
                 'status', 'type', 'created_time']


class ReceivingViewSet(BaseModelSet):
    """入库管理"""

    queryset = Receiving.objects.all()
    serializer_class = ReceivingSerializer
    ordering_fields = ['created_time']
    filterset_class = ReceivingViewSetFilter
    pagination_class = DynamicPageNumber(1000)

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
