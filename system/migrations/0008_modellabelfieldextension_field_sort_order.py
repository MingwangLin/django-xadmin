# Generated by Django 5.1.4 on 2025-01-22 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_menumeta_active_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='modellabelfieldextension',
            name='field_sort_order',
            field=models.IntegerField(default=1, verbose_name='排序'),
        ),
    ]
