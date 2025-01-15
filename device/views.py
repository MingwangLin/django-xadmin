from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.response import Response

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from common.core.pagination import DynamicPageNumber
from device.models import Device, Channel, DeviceChannel
from device.serializers import DeviceSerializer, ChannelSerializer, DeviceChannelSerializer


class ChannelViewSetFilter(BaseFilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status')
    stream_status = filters.CharFilter(field_name='stream_status')

    class Meta:
        model = Channel
        fields = ['name', 'status', 'stream_status', 'created_time']


class ChannelViewSet(BaseModelSet, ImportExportDataAction):
    """通道管理"""
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    ordering_fields = ['created_time']
    filterset_class = ChannelViewSetFilter
    pagination_class = DynamicPageNumber(1000)


class DeviceViewSetFilter(BaseFilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    device_id = filters.CharFilter(field_name='device_id', lookup_expr='icontains')
    manufacturer = filters.CharFilter(field_name='manufacturer', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type')
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = Device
        fields = ['name', 'device_id', 'manufacturer', 'type', 'status', 'is_bound', 'created_time']


class DeviceViewSet(BaseModelSet, ImportExportDataAction):
    """设备管理"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    ordering_fields = ['created_time']
    filterset_class = DeviceViewSetFilter
    pagination_class = DynamicPageNumber(1000)

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


class DeviceChannelViewSet(BaseModelSet):
    """设备通道关联"""
    queryset = DeviceChannel.objects.all()
    serializer_class = DeviceChannelSerializer
    ordering_fields = ['created_time']
    pagination_class = DynamicPageNumber(1000)

    def get_queryset(self):
        queryset = super().get_queryset()
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        return queryset 