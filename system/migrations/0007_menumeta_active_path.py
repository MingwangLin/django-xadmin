# Generated by Django 5.1.4 on 2025-01-21 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_alter_modelseparationfield_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='menumeta',
            name='active_path',
            field=models.CharField(blank=True, help_text='Path pattern used for menu highlighting', max_length=255, null=True, verbose_name='Active path'),
        ),
    ]
