from rest_framework import viewsets
from .models import Device
from .serializers import DeviceSerializer
from common.core.modelset import BaseModelSet, ImportExportDataAction

class DeviceViewSet(BaseModelSet, ImportExportDataAction):
    """设备"""  
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'serial_number']
    ordering_fields = ['name', 'created_at', 'updated_at'] 