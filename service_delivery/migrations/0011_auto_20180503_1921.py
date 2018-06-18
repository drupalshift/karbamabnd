# Generated by Django 2.0.2 on 2018-05-03 19:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.query_utils
import django_jalali.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('service_delivery', '0010_auto_20180430_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseservice',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='مشتری'),
        ),
        migrations.AlterField(
            model_name='baseservice',
            name='schedule_time',
            field=django_jalali.db.models.jDateTimeField(blank=True, null=True, verbose_name='زمان ارائه خدمت'),
        ),
        migrations.AlterField(
            model_name='baseservice',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'در حال بررسی'), (2, 'در حال انجام'), (3, 'انجام شده'), (4, 'لفو شده توسط مشتری'), (5, 'لفو شده توسط سرویس\u200cدهنده')], default=1, null=True, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='servicedetail',
            name='content_type',
            field=models.OneToOneField(blank=True, limit_choices_to=django.db.models.query_utils.Q(django.db.models.query_utils.Q(('model', 'DryCleaning'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'CarpetCleaning'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'AC'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Medical'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Towing'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'HomeAppliance'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Plumbing'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Electricity'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Tuition'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Truck'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Cleaning'), ('app_label', 'service_delivery'), _connector='AND'), _connector='OR'), null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
    ]
