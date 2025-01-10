#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : field
# author : ly_13
# date : 8/10/2024

from django.db import models
from django.utils.translation import gettext_lazy as _

from common.core.models import DbAuditModel, DbUuidModel


class ModelLabelField(DbAuditModel, DbUuidModel):
    class KeyChoices(models.TextChoices):
        TEXT = 'value.text', _('Text')
        JSON = 'value.json', _('Json')
        ALL = 'value.all', _('All data')
        DATETIME = 'value.datetime', _('Datetime')
        DATETIME_RANGE = 'value.datetime.range', _('Datetime range selector')
        DATE = 'value.date', _('Seconds to the current time')
        OWNER = 'value.user.id', _('My ID')
        OWNER_DEPARTMENT = 'value.user.dept.id', _('My department ID')
        OWNER_DEPARTMENTS = 'value.user.dept.ids', _('My department ID and data below the department')
        DEPARTMENTS = 'value.dept.ids', _('Department ID and data below the department')
        TABLE_USER = 'value.table.user.ids', _('Select the user ID')
        TABLE_MENU = 'value.table.menu.ids', _('Select menu ID')
        TABLE_ROLE = 'value.table.role.ids', _('Select role ID')
        TABLE_DEPT = 'value.table.dept.ids', _('Select department ID')

    class FieldChoices(models.IntegerChoices):
        ROLE = 0, _("Role permission")
        DATA = 1, _("Data permission")

    field_type = models.SmallIntegerField(choices=FieldChoices, default=FieldChoices.DATA, verbose_name=_("Field type"))
    parent = models.ForeignKey('system.ModelLabelField', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name=_("Parent node"))
    name = models.CharField(verbose_name=_("Model/Field name"), max_length=128)
    label = models.CharField(verbose_name=_("Model/Field label"), max_length=128)

    class Meta:
        ordering = ('-created_time',)
        unique_together = ('name', 'parent')
        verbose_name = _("Model label field")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.label}({self.name})"


class ModelLabelFieldExtension(DbAuditModel, DbUuidModel):
    field = models.OneToOneField('system.ModelLabelField', on_delete=models.CASCADE, verbose_name=_("Field"))
    align = models.CharField(max_length=32, null=True, blank=True, verbose_name="对齐方式")
    width = models.IntegerField(null=True, blank=True, verbose_name="宽度")
    table_visible = models.BooleanField(null=True, blank=True, verbose_name="表格是否可见")
    table_sortable = models.CharField(max_length=32, null=True, blank=True, verbose_name="表格排序")
    table_merge = models.BooleanField(null=True, blank=True, verbose_name="表格合并")
    form_visible = models.BooleanField(null=True, blank=True, verbose_name="表单是否可见")
    form_is_search = models.BooleanField(null=True, blank=True, verbose_name="是否为搜索字段")
    form_is_filter = models.BooleanField(null=True, blank=True, verbose_name="是否为过滤字段")
    form_is_batch_edit = models.BooleanField(null=True, blank=True, verbose_name="是否为批量编辑字段")
    form_placehold = models.CharField(max_length=128, null=True, blank=True, verbose_name="表单占位符")
    form_grid = models.IntegerField(null=True, blank=True, verbose_name="表单栅格")
    form_rules = models.CharField(max_length=256, null=True, blank=True, verbose_name="表单校验规则")

    class Meta:
        ordering = ('-created_time',)
        verbose_name = _("Model label field extension")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.field.label}({self.field.name}) Extension"
