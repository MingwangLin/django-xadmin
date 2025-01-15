from django.contrib import admin
from .models import Device, Channel, DeviceChannel


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_id', 'status', 'created_time', 'updated_time']
    list_filter = ['status', 'created_time', 'type']
    search_fields = ['name', 'device_id', 'manufacturer']
    readonly_fields = ['created_time', 'updated_time']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'stream_status', 'created_time']
    list_filter = ['status', 'stream_status', 'created_time']
    search_fields = ['name', 'playlist_name']
    readonly_fields = ['created_time', 'updated_time']


@admin.register(DeviceChannel)
class DeviceChannelAdmin(admin.ModelAdmin):
    list_display = ['device', 'channel', 'is_active', 'created_time']
    list_filter = ['is_active', 'created_time']
    search_fields = ['device__name', 'channel__name']
    readonly_fields = ['created_time', 'updated_time'] 