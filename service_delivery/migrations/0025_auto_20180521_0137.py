# Generated by Django 2.0.2 on 2018-05-21 01:37

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.query_utils


class Migration(migrations.Migration):

    dependencies = [
        ('service_delivery', '0024_auto_20180521_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicedetail',
            name='content_type',
            field=models.OneToOneField(blank=True, limit_choices_to=django.db.models.query_utils.Q(django.db.models.query_utils.Q(('model', 'DryCleaning'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'CarpetCleaning'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'AC'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Medical'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Towing'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'HomeAppliance'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Plumbing'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Electricity'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Tuition'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Truck'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Cleaning'), ('app_label', 'service_delivery'), _connector='AND'), _connector='OR'), null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
    ]