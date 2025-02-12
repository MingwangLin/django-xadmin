from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VenueLetter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fileName', models.CharField(max_length=255)),
                ('key', models.CharField(max_length=255)),
                ('auditUserId', models.IntegerField()),
                ('uploadTime', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BatchOverview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taskIssueDate', models.DateField(null=True)),
            ],
        ),
    ] 