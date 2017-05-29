from django.db import models
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
# Create your models here.


class AutomationJob(models.Model):
    DATATYPE_CHOICES = Choices(
        ('LAZ', _('LAZ')),
        ('Ortho', _('ORTHO')),
        ('DTM', _('DTM')),
        ('DSM', _('DSM')),
        ('Others', _('Others'))
    )

    PROCESSOR_CHOICES = Choices(
        ('DRM', _('DREAM')),
        ('PL1', _('Phil-LiDAR 1')),
        ('PL2', _('Phil-LiDAR 2')),
    )

    STATUS_CHOICES = Choices(
        ('pending_process', _('Pending Job')),
        ('done_process', _('Processing Job')),
        ('pending_ceph', _('Uploading in Ceph')),
        ('done_ceph', _('Uploaded in Ceph')),
        ('done', _('Uploaded in LiPAD')),
        # (-1, 'error', _('Error')),
    )

    OS_CHOICES = Choices(
        ('linux', _('Process in Linux')),
        ('windows', _('Process in Windows')),
    )

    datatype = models.CharField(
        choices=DATATYPE_CHOICES,
        max_length=10,
        help_text=_('Datatype of input'),
    )

    input_dir = models.TextField(
        _('Input Directory'),
        blank=False,
        null=False,
        help_text=_('Full path of directory location in server')
    )

    output_dir = models.TextField(
        _('Output Directory'),
        blank=False,
        null=False,
        help_text=_('Folder location in server')
    )

    processor = models.CharField(
        _('Data Processor'),
        choices=PROCESSOR_CHOICES,
        max_length=10,
    )

    date_submitted = models.DateTimeField(
        default=datetime.now,
        blank=False,
        null=False,
        help_text=_('The date when the job was submitted in LiPAD')
    )

    status = models.CharField(
        _('Job status'),
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES.pending_process,
        max_length=20
    )

    status_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('The date when the status was updated'),
        default=datetime.now()
    )

    target_os = models.CharField(
        _('OS to Process Job'),
        choices=OS_CHOICES,
        default=OS_CHOICES.linux,
        max_length=20
    )

    log = models.TextField(null=False, blank=True)

    def __unicode__(self):
        return "{0} {1} {2}". \
            format(self.datatype, self.date_submitted, self.status)

class DemDataStore(models.Model):
    demid   = models.IntegerField(primary_key=True)
    name    = models.CharField(max_length=20)
    suc     = models.CharField(max_length=5)
    type    = models.CharField(max_length=5)
    shifting_val_x = models.FloatField() 
    shifting_val_y = models.FloatField() 
    shifting_val_z = models.FloatField()
    height_diff    = models.FloatField()
    rmse           = models.FloatField()
    dem_file_path  = models.TextField(null=False)
    block_name_list = models.TextField(null=False)