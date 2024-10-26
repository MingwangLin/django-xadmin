#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : modelfield
# author : ly_13
# date : 10/24/2024
from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _

from common.core.models import DbAuditModel
from common.core.serializers import BaseModelSerializer
from common.core.utils import PrintLogFormat
from common.utils import get_logger
from system.models import ModelLabelField

logger = get_logger(__name__)


def get_sub_serializer_fields():
    cls_list = []
    activate(settings.LANGUAGE_CODE)

    def get_all_subclass(base_cls):
        if base_cls.__subclasses__():
            for cls in base_cls.__subclasses__():
                cls_list.append(cls)
                get_all_subclass(cls)

    get_all_subclass(BaseModelSerializer)

    delete = False
    now = timezone.now()
    field_type = ModelLabelField.FieldChoices.ROLE
    for cls in cls_list:
        instance = cls(ignore_field_permission=True)
        model = instance.Meta.model
        if not model:
            continue
        count = [0, 0]

        delete = True
        obj, created = ModelLabelField.objects.update_or_create(name=model._meta.label_lower, field_type=field_type,
                                                                parent=None,
                                                                defaults={'label': model._meta.verbose_name})
        count[int(not created)] += 1
        for name, field in instance.fields.items():
            _, created = ModelLabelField.objects.update_or_create(name=name, parent=obj, field_type=field_type,
                                                                  defaults={'label': field.label})
            count[int(not created)] += 1
        PrintLogFormat(f"Model:({model._meta.label_lower})").warning(
            f"update_or_create role permission, created:{count[0]} updated:{count[1]}")

    if delete:
        deleted, _rows_count = ModelLabelField.objects.filter(field_type=field_type, updated_time__lt=now).delete()
        PrintLogFormat(f"Sync Role permission end").info(f"deleted success, deleted:{deleted} row_count {_rows_count}")


def get_app_model_fields():
    delete = False
    now = timezone.now()
    field_type = ModelLabelField.FieldChoices.DATA
    obj, created = ModelLabelField.objects.update_or_create(name=f"*", field_type=field_type,
                                                            defaults={'label': _("All tables")}, parent=None)
    ModelLabelField.objects.update_or_create(name=f"*", field_type=field_type, parent=obj,
                                             defaults={'label': _("All fields")})

    for field in DbAuditModel._meta.fields:
        ModelLabelField.objects.update_or_create(name=field.name, field_type=field_type, parent=obj,
                                                 defaults={'label': getattr(field, 'verbose_name', field.name)})

    for app_name, app in apps.app_configs.items():
        if app_name not in settings.PERMISSION_DATA_AUTH_APPS:
            continue

        for model in app.models.values():
            count = [0, 0]
            delete = True
            model_name = model._meta.model_name
            verbose_name = model._meta.verbose_name
            if not hasattr(model, 'Meta'):  # 虚拟 model 判断, 不包含Meta的模型，是系统生成的第三方模型，包含 relationship
                continue
            obj, created = ModelLabelField.objects.update_or_create(name=f"{app_name}.{model_name}",
                                                                    field_type=field_type,
                                                                    parent=None, defaults={'label': verbose_name})
            count[int(not created)] += 1
            # for field in model._meta.get_fields():
            for field in model._meta.fields:
                _obj, created = ModelLabelField.objects.update_or_create(name=field.name, parent=obj,
                                                                         field_type=field_type,
                                                                         defaults={'label': field.verbose_name})
                count[int(not created)] += 1
            PrintLogFormat(f"Model:({app_name}.{model_name})").warning(
                f"update_or_create data permission, created:{count[0]} updated:{count[1]}")
    if delete:
        deleted, _rows_count = ModelLabelField.objects.filter(field_type=field_type, updated_time__lt=now).delete()
        PrintLogFormat(f"Sync Data permission end").info(f"deleted success, deleted:{deleted} row_count {_rows_count}")


@transaction.atomic
def sync_model_field():
    """
    用于执行迁移命令的时候，同步字段数据到数据库
    """
    activate(settings.LANGUAGE_CODE)
    get_app_model_fields()
    get_sub_serializer_fields()