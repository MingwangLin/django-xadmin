import json

from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.response import Response

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from common.core.pagination import DynamicPageNumber
from common.core.queryset_helper import QuerysetHelper
from common.core.response import ApiResponse
from device.models import Device, Channel, DeviceChannel
from device.serializers import DeviceSerializer, ChannelSerializer, DeviceChannelSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.plumbing import build_array_type, build_basic_type


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
        fields = ['name', 'device_id', 'manufacturer', 'type', 'status', 'is_bound', 'created_time', 'remark']


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
class DeviceViewSet(BaseModelSet, ImportExportDataAction):
    """设备管理"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    ordering_fields = ['created_time']
    filterset_class = DeviceViewSetFilter
    pagination_class = DynamicPageNumber(1000)
    model = Device
    filter_fields = ['name', 'device_id', 'manufacturer', 'type', 'status', 'is_bound', 'created_time', 'remark']

    def get_queryset(self):
        queryset = super().get_queryset()
        request_data = self.request.query_params
        filter_dict = QuerysetHelper.get_filter_dict(request_data)
        queryset = QuerysetHelper.apply_filter(queryset, filter_dict)
        queryset = QuerysetHelper.get_general_sort_kyes_filtered_queryset(request_data, queryset, self.model)
        queryset = QuerysetHelper.get_search_text_multiple_filtered_queryset(request_data, queryset, self.filter_fields)
        return queryset 
    
    @action(methods=['POST'], detail=False)
    def query(self, request, *args, **kwargs):
        # Create a new QueryDict with request.data
        query_dict = request.query_params.copy()
        for key, value in request.data.items():
            if key in ['filter', 'sortkeys']:
                if value is not None:
                    query_dict[key] = json.dumps(value)
                else:
                    query_dict[key] = ''
            elif isinstance(value, list):
                query_dict.setlist(key, value)
            else:
                query_dict[key] = value
                
        request._request.GET = query_dict  # Set the underlying GET parameters
        return self.list(request, *args, **kwargs)

    @action(methods=['POST'], detail=True)
    def bind_channel(self, request, *args, **kwargs):
        """绑定通道"""
        try:
            device = self.get_object()
            
            # Get OSS helper instance
            from common.core.oss_helper import OSSHelper
            import oss2
            
            osshelper = OSSHelper()
            bucket = osshelper.get_bucket_instance()
            
            # Generate unique channel name using device ID and timestamp
            from django.utils import timezone
            import datetime
            
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            channel_name = f"channel_{device.device_id}_{timestamp}"
            playlist_name = f"{channel_name}.m3u8"
            
            # Create OSS live channel
            create_result = bucket.create_live_channel(
                channel_name,
                oss2.models.LiveChannelInfo(
                    status='enabled',
                    description=f'Live channel for device {device.device_id}',
                    target=oss2.models.LiveChannelInfoTarget(
                        playlist_name=playlist_name,
                        frag_count=3,
                        frag_duration=5
                    )
                )
            )
            
            # Create Channel in database
            channel = Channel.objects.create(
                name=channel_name,
                playlist_name=playlist_name,
                status=Channel.StatusChoices.ENABLED,
                stream_status=Channel.StreamStatusChoices.OFFLINE,
                url=create_result.publish_url,  # Store the RTMP URL
                frag_count=3,
                frag_duration=5,
                expired=timezone.now() + datetime.timedelta(days=365)  # Set expiration to 1 year
            )
            
            # Deactivate existing device channel associations
            DeviceChannel.objects.filter(device=device, is_active=True).update(is_active=False)
            
            # Create new device channel association
            DeviceChannel.objects.create(
                device=device,
                channel=channel,
                is_active=True
            )
            
            # Update device bound status
            device.is_bound = True
            device.save()
            
            return ApiResponse(data={
                'success': True,
                'channel': ChannelSerializer(channel).data,
                'publish_url': create_result.publish_url,
                'play_url': create_result.play_url
            })
            
        except Exception as e:
            return ApiResponse(detail=str(e), code=400, status=400)


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