from django.db import models
from django.utils.translation import gettext_lazy as _

from common.core.models import DbAuditModel, DbUuidModel


class ProjectBatch(DbAuditModel, DbUuidModel):
    class ClassificationChoices(models.TextChoices):
        OFFICIAL = 'official', _('Official')
        ESTIMATED = 'estimated', _('Estimated')

    class CategoryChoices(models.TextChoices):
        TEST = 'test', _('Test')
        FORMAL = 'formal', _('Formal')

    class SceneTypeChoices(models.TextChoices):
        ETX = 'etx', _('ETX')
        SZ = 'sz', _('SZ')
        JOYTEST = 'joytest', _('Joy Test')
        OFFLINE = 'offline', _('Offline Arrangement')
        NONE = 'none', _('None')

    class StatusChoices(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In Progress')
        FINISHED = 'finished', _('Finished')

    class ExamTypeChoices(models.IntegerChoices):
        PaperExam = 0, _('纸笔考')
        PcExam = 1, _('机考')
        Other = 2, _('其它')

    name = models.CharField(verbose_name=_('Batch Name'), max_length=256, null=True, blank=True)
    code = models.CharField(verbose_name=_('Batch Code'), max_length=50, null=True, blank=True)
    ets_code = models.CharField(verbose_name=_('ETS Code'), max_length=50, null=True, blank=True)
    short_name = models.CharField(verbose_name=_('Short Name'), max_length=50, null=True, blank=True)
    exam_type = models.IntegerField(
        verbose_name=_('Exam Type'),
        choices=ExamTypeChoices.choices,
        null=True,
        blank=True
    )
    category = models.CharField(
        verbose_name=_('Category'),
        max_length=32,
        choices=CategoryChoices.choices,
        default=CategoryChoices.FORMAL
    )
    classification = models.CharField(
        verbose_name=_('Classification'),
        max_length=32,
        choices=ClassificationChoices.choices,
        default=ClassificationChoices.OFFICIAL
    )
    scene_type = models.CharField(
        verbose_name=_('Scene Type'),
        max_length=50,
        choices=SceneTypeChoices.choices,
        null=True,
        blank=True
    )
    invigilator_type = models.CharField(verbose_name=_('Invigilator Type'), max_length=50, null=True, blank=True)
    exam_begin_date = models.DateField(verbose_name=_('Exam Begin Date'), null=True, blank=True, db_index=True)
    exam_end_date = models.DateField(verbose_name=_('Exam End Date'), null=True, blank=True)
    confirm_begin_date = models.DateField(verbose_name=_('Confirm Begin Date'), null=True, blank=True)
    confirm_end_date = models.DateField(verbose_name=_('Confirm End Date'), null=True, blank=True)
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS
    )
    demands = models.JSONField(verbose_name=_('Exam Requirements'), null=True, blank=True)
    tags = models.JSONField(verbose_name=_('Tags'), null=True, blank=True)
    sync_timestamp = models.CharField(verbose_name=_('Sync Timestamp'), max_length=50, null=True, blank=True)
    sync_allowed = models.IntegerField(verbose_name=_('Sync Allowed'), default=1)
    sync_time = models.DateTimeField(verbose_name=_('Sync Time'), null=True, blank=True)
    remote_configs = models.JSONField(verbose_name=_('Remote Configs'), null=True, blank=True)
    manager = models.CharField(verbose_name=_('Manager'), max_length=50, null=True, blank=True)
    project_name = models.CharField(verbose_name=_('Project Name'), max_length=256, null=True, blank=True)
    project_code = models.CharField(verbose_name=_('Project Code'), max_length=50, null=True, blank=True)
    start_department = models.CharField(verbose_name=_('Start Department'), max_length=50, null=True, blank=True)
    department = models.CharField(verbose_name=_('Business Department'), max_length=50, null=True, blank=True)
    project_department = models.CharField(verbose_name=_('Project Department'), max_length=50, null=True, blank=True)
    schedule_count = models.IntegerField(verbose_name=_('Schedule Count'), null=True, blank=True)
    total_exam_rooms = models.IntegerField(verbose_name=_('Total Exam Rooms'), null=True, blank=True)
    online_exam_rooms = models.IntegerField(verbose_name=_('Online Exam Rooms'), null=True, blank=True)
    stream_start_time = models.DateTimeField(verbose_name=_('Stream Start Time'), null=True, blank=True)
    stream_end_time = models.DateTimeField(verbose_name=_('Stream End Time'), null=True, blank=True)
    enable_ai_monitoring = models.BooleanField(verbose_name=_('Enable AI Monitoring'), default=False)
    show_ata_watermark = models.BooleanField(verbose_name=_('Show ATA Watermark'), default=False)
    video_display_text = models.CharField(verbose_name=_('Video Display Text'), max_length=256, null=True, blank=True)
    videos_per_room = models.IntegerField(verbose_name=_('Videos Per Room'), null=True, blank=True)

    class Meta:
        verbose_name = _('Project Batch')
        verbose_name_plural = _('Project Batches')
        ordering = ('-created_time',)

    def __str__(self):
        return f"{self.name or 'Unnamed Batch'} ({self.code})"
