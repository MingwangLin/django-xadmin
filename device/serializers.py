from rest_framework import serializers

from common.core.serializers import BaseModelSerializer
from common.fields.utils import input_wrapper
from device import models


class ChannelSerializer(BaseModelSerializer):
    class Meta:
        model = models.Channel
        fields = [
            'pk', 'name', 'playlist_name', 'status', 'stream_status', 'url',
            'expired', 'frag_count', 'frag_duration', 'created_time', 'updated_time'
        ]
        table_fields = [
            'pk', 'name', 'status', 'stream_status', 'url', 'expired'
        ]
        extra_kwargs = {
            'pk': {'read_only': True},
        }


class DeviceSerializer(BaseModelSerializer):

    class Meta:
        model = models.Device
        fields = [
            'pk', 'device_id', 'manufacturer', 'name', 'type', 'status',
            'playlist_name', 'is_bound', 'remark', 'channels', 'created_time', 'updated_time'
        ]
        table_fields = [
            'pk', 'device_id', 'name', 'type', 'status', 'is_bound', 'created_time'
        ]
        extra_kwargs = {
            'pk': {'read_only': True},
            'channels': {
                'label': '关联通道',
            }
        }


class DeviceChannelSerializer(BaseModelSerializer):
    class Meta:
        model = models.DeviceChannel
        fields = [
            'pk', 'device', 'channel', 'is_active', 'created_time', 'updated_time'
        ]
        table_fields = [
            'pk', 'device', 'channel', 'is_active'
        ]
        extra_kwargs = {
            'pk': {'read_only': True},
            'device': {
                'attrs': ['pk', 'name'],
                'required': True,
                'format': "{name}({pk})"
            },
            'channel': {
                'attrs': ['pk', 'name'],
                'required': True,
                'format': "{name}({pk})"
            }
        } 