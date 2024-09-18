# Generated by Django 5.1.1 on 2024-09-17 11:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('notifications', '0001_initial'),
        ('system', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='messagecontent',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='creator_query', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='messagecontent',
            name='dept_belong',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='dept_belong_query', to='system.deptinfo', verbose_name='Data ownership department'),
        ),
        migrations.AddField(
            model_name='messagecontent',
            name='file',
            field=models.ManyToManyField(to='system.uploadfile', verbose_name='Uploaded attachments'),
        ),
        migrations.AddField(
            model_name='messagecontent',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='modifier_query', to=settings.AUTH_USER_MODEL, verbose_name='Modifier'),
        ),
        migrations.AddField(
            model_name='messagecontent',
            name='notice_dept',
            field=models.ManyToManyField(blank=True, null=True, to='system.deptinfo', verbose_name='The notified department'),
        ),
        migrations.AddField(
            model_name='messagecontent',
            name='notice_role',
            field=models.ManyToManyField(blank=True, null=True, to='system.userrole', verbose_name='The notified role'),
        ),
        migrations.AddField(
            model_name='messageuserread',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='creator_query', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='messageuserread',
            name='dept_belong',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='dept_belong_query', to='system.deptinfo', verbose_name='Data ownership department'),
        ),
        migrations.AddField(
            model_name='messageuserread',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='modifier_query', to=settings.AUTH_USER_MODEL, verbose_name='Modifier'),
        ),
        migrations.AddField(
            model_name='messageuserread',
            name='notice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.messagecontent', verbose_name='Notice'),
        ),
        migrations.AddField(
            model_name='messageuserread',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='messagecontent',
            name='notice_user',
            field=models.ManyToManyField(blank=True, null=True, through='notifications.MessageUserRead', to=settings.AUTH_USER_MODEL, verbose_name='The notified user'),
        ),
        migrations.AddField(
            model_name='systemmsgsubscription',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='creator_query', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='systemmsgsubscription',
            name='dept_belong',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='dept_belong_query', to='system.deptinfo', verbose_name='Data ownership department'),
        ),
        migrations.AddField(
            model_name='systemmsgsubscription',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='modifier_query', to=settings.AUTH_USER_MODEL, verbose_name='Modifier'),
        ),
        migrations.AddField(
            model_name='systemmsgsubscription',
            name='users',
            field=models.ManyToManyField(related_name='system_msg_subscriptions', to=settings.AUTH_USER_MODEL,
                                         verbose_name='User'),
        ),
        migrations.AddField(
            model_name='usermsgsubscription',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='creator_query', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='usermsgsubscription',
            name='dept_belong',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='dept_belong_query', to='system.deptinfo', verbose_name='Data ownership department'),
        ),
        migrations.AddField(
            model_name='usermsgsubscription',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='modifier_query', to=settings.AUTH_USER_MODEL, verbose_name='Modifier'),
        ),
        migrations.AddField(
            model_name='usermsgsubscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                    verbose_name='User'),
        ),
        migrations.AddIndex(
            model_name='messageuserread',
            index=models.Index(fields=['owner', 'unread'], name='notificatio_owner_i_fd088f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='messageuserread',
            unique_together={('owner', 'notice')},
        ),
        migrations.AlterUniqueTogether(
            name='usermsgsubscription',
            unique_together={('user', 'message_type')},
        ),
    ]