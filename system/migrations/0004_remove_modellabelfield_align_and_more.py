# Generated by Django 5.1.4 on 2025-01-10 06:14

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_modellabelfield_align_modellabelfield_form_grid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modellabelfield',
            name='align',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_grid',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_is_batch_edit',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_is_filter',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_is_search',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_placehold',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_rules',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='form_visible',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='table_merge',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='table_sortable',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='table_visible',
        ),
        migrations.RemoveField(
            model_name='modellabelfield',
            name='width',
        ),
        migrations.CreateModel(
            name='ModelLabelFieldExtension',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created time')),
                ('updated_time', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated time')),
                ('description', models.CharField(blank=True, max_length=256, null=True, verbose_name='Description')),
                ('align', models.CharField(blank=True, max_length=32, null=True, verbose_name='对齐方式')),
                ('width', models.IntegerField(blank=True, null=True, verbose_name='宽度')),
                ('table_visible', models.BooleanField(blank=True, null=True, verbose_name='表格是否可见')),
                ('table_sortable', models.CharField(blank=True, max_length=32, null=True, verbose_name='表格排序')),
                ('table_merge', models.BooleanField(blank=True, null=True, verbose_name='表格合并')),
                ('form_visible', models.BooleanField(blank=True, null=True, verbose_name='表单是否可见')),
                ('form_is_search', models.BooleanField(blank=True, null=True, verbose_name='是否为搜索字段')),
                ('form_is_filter', models.BooleanField(blank=True, null=True, verbose_name='是否为过滤字段')),
                ('form_is_batch_edit', models.BooleanField(blank=True, null=True, verbose_name='是否为批量编辑字段')),
                ('form_placehold', models.CharField(blank=True, max_length=128, null=True, verbose_name='表单占位符')),
                ('form_grid', models.IntegerField(blank=True, null=True, verbose_name='表单栅格')),
                ('form_rules', models.CharField(blank=True, max_length=256, null=True, verbose_name='表单校验规则')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='creator_query', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('dept_belong', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='dept_belong_query', to='system.deptinfo', verbose_name='Data ownership department')),
                ('field', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='system.modellabelfield', verbose_name='Field')),
                ('modifier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='modifier_query', to=settings.AUTH_USER_MODEL, verbose_name='Modifier')),
            ],
            options={
                'verbose_name': 'Model label field extension',
                'verbose_name_plural': 'Model label field extension',
                'ordering': ('-created_time',),
            },
        ),
    ]
