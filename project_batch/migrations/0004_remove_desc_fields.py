# Generated by Django 5.1.4 on 2025-01-16 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_batch', '0003_projectbatch_online_exam_rooms_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectbatch',
            name='exam_type',
            field=models.IntegerField(blank=True, choices=[(0, '纸笔考'), (1, '机考'), (2, '其它')], null=True, verbose_name='Exam Type'),
        ),
    ]
