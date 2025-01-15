from django.db import models
from django.utils.translation import gettext_lazy as _

from common.core.models import DbAuditModel, DbUuidModel


class Channel(DbAuditModel, DbUuidModel):
    class StatusChoices(models.TextChoices):
        ENABLED = 'enabled', _('Enabled')
        DISABLED = 'disabled', _('Disabled')

    class StreamStatusChoices(models.TextChoices):
        ONLINE = 'live', _('Online')
        OFFLINE = 'offline', _('Offline')

    name = models.CharField(verbose_name=_('Channel Name'), max_length=128, null=True, blank=True)
    playlist_name = models.CharField(verbose_name=_('M3U8 File Name'), max_length=128, null=True, blank=True)
    status = models.CharField(
        verbose_name=_('Channel Status'),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ENABLED
    )
    stream_status = models.CharField(
        verbose_name=_('Stream Status'),
        max_length=20,
        choices=StreamStatusChoices.choices,
        default=StreamStatusChoices.OFFLINE
    )
    url = models.CharField(verbose_name=_('Stream URL'), max_length=128, null=True, blank=True)
    expired = models.DateTimeField(verbose_name=_('Expiration Time'), null=True, blank=True)
    frag_count = models.IntegerField(verbose_name=_('TS File Count'), null=True, blank=True)
    frag_duration = models.IntegerField(verbose_name=_('TS File Duration'), null=True, blank=True)

    class Meta:
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        ordering = ('-created_time',)

    def __str__(self):
        return f"{self.name or 'Unnamed Channel'}"


class Device(DbAuditModel, DbUuidModel):
    class TypeChoices(models.TextChoices):
        IPC = 'IPC', _('IPC')
        PATROL = 'patrol', _('Patrol Assistant')

    class StreamStatusChoices(models.TextChoices):
        ONLINE = 'live', _('Online')
        OFFLINE = 'offline', _('Offline')

    device_id = models.CharField(verbose_name=_('Device ID'), max_length=64, unique=True)
    manufacturer = models.CharField(verbose_name=_('Manufacturer'), max_length=64, null=True, blank=True)
    name = models.CharField(verbose_name=_('Device Name'), max_length=128, null=True, blank=True)
    type = models.CharField(
        verbose_name=_('Device Type'),
        max_length=20,
        choices=TypeChoices.choices,
        default=TypeChoices.IPC
    )
    status = models.CharField(
        verbose_name=_('Stream Status'),
        max_length=20,
        choices=StreamStatusChoices.choices,
        default=StreamStatusChoices.OFFLINE
    )
    playlist_name = models.CharField(verbose_name=_('Main M3U8 File Name'), max_length=128, null=True, blank=True)
    is_bound = models.BooleanField(verbose_name=_('Is Bound'), default=False)
    remark = models.TextField(verbose_name=_('Remarks'), null=True, blank=True)
    channels = models.ManyToManyField(
        'Channel',
        through='DeviceChannel',
        verbose_name=_('Channels'),
        related_name='devices'
    )

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        ordering = ('-created_time',)
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class DeviceChannel(DbAuditModel):
    device = models.ForeignKey(
        'Device',
        on_delete=models.CASCADE,
        related_name='device_channels',
        verbose_name=_('Device')
    )
    channel = models.ForeignKey(
        'Channel',
        on_delete=models.CASCADE,
        related_name='device_channels',
        verbose_name=_('Channel')
    )
    is_active = models.BooleanField(verbose_name=_('Is Active'), default=True)

    class Meta:
        verbose_name = _('Device Channel')
        verbose_name_plural = _('Device Channels')
        ordering = ('-created_time',)
        unique_together = ['device', 'channel']
        indexes = [
            models.Index(fields=['device', 'is_active']),
            models.Index(fields=['channel', 'is_active']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.channel.name}" 