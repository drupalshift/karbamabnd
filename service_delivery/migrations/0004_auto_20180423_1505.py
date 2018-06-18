# Generated by Django 2.0.2 on 2018-04-23 15:05

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.query_utils
import django_smalluuid.models


class Migration(migrations.Migration):

    dependencies = [
        ('service_delivery', '0003_auto_20180423_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='default_city',
        ),
        migrations.AddField(
            model_name='announcement',
            name='is_ad',
            field=models.BooleanField(default=False, verbose_name='تبلیغ'),
        ),
        migrations.AddField(
            model_name='drycleaning',
            name='delivery_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='زمان تحویل'),
        ),
        migrations.AddField(
            model_name='drycleaning',
            name='is_express',
            field=models.BooleanField(default=False, verbose_name='تحوبل اکسپرس'),
        ),
        migrations.AddField(
            model_name='personnel',
            name='ratings',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='امتیاز'),
        ),
        migrations.AddField(
            model_name='personnel',
            name='ratings_count',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='تعداد امتیازات'),
        ),
        migrations.AddField(
            model_name='servicedetail',
            name='ban_item',
            field=models.TextField(blank=True, null=True, verbose_name='موارد غیر فعال'),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 'بندرعباس'), (2, 'کرمان'), (3, 'یزد')], default=1, null=True, verbose_name='شهر'),
        ),
        migrations.AddField(
            model_name='user',
            name='credit',
            field=models.FloatField(blank=True, null=True, verbose_name='اعتبار'),
        ),
        migrations.AlterField(
            model_name='servicedetail',
            name='content_type',
            field=models.OneToOneField(blank=True, limit_choices_to=django.db.models.query_utils.Q(django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'DryCleaning'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'CarpetCleaning'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'AC'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Medical'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Towing'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'HomeAppliance'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Plumbing'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Electricity'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Tuition'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Truck'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Cleaning'), _connector='AND'), _connector='OR'), null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
    ]