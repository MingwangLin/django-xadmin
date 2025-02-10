from django.db import models
from django.utils.translation import gettext_lazy as _

from common.core.models import DbAuditModel, DbUuidModel


class Region(DbAuditModel, DbUuidModel):
    class TypeChoices(models.IntegerChoices):
        COUNTRY = 1, _('Country')
        PROVINCE = 2, _('Province')
        CITY = 3, _('City')
        DISTRICT = 4, _('District')

    class StatusChoices(models.TextChoices):
        ENABLED = 'enabled', _('Enabled')
        DISABLED = 'disabled', _('Disabled')

    code = models.CharField(
        verbose_name=_('Region Code'),
        max_length=128
    )
    name = models.CharField(
        verbose_name=_('Region Name'),
        max_length=128
    )
    full_name = models.CharField(
        verbose_name=_('Full Name'),
        max_length=512,
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        verbose_name=_('Parent Region'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    type = models.IntegerField(
        verbose_name=_('Region Type'),
        choices=TypeChoices.choices,
        null=True,
        blank=True
    )
    sort_order = models.IntegerField(
        verbose_name=_('Sort Order'),
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        blank=True
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ENABLED
    )
    tree_code = models.CharField(
        verbose_name=_('Tree Code'),
        max_length=128,
        null=True,
        blank=True
    )
    is_capital = models.BooleanField(
        verbose_name=_('Is Capital'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        ordering = ('sort_order', 'created_time')
        indexes = [
            models.Index(fields=['parent', 'id']),
            models.Index(fields=['name', 'type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
