# Generated by Django 2.0.2 on 2018-04-30 21:19

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.query_utils


class Migration(migrations.Migration):

    dependencies = [
        ('service_delivery', '0009_auto_20180428_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseservice',
            name='used_discount',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.DiscountCoupon', verbose_name='تخفیف'),
        ),
        migrations.AlterField(
            model_name='servicedetail',
            name='content_type',
            field=models.OneToOneField(blank=True, limit_choices_to=django.db.models.query_utils.Q(django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'DryCleaning'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'CarpetCleaning'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'AC'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Medical'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Towing'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'HomeAppliance'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Plumbing'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Electricity'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Tuition'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Truck'), _connector='AND'), django.db.models.query_utils.Q(('app_label', 'service_delivery'), ('model', 'Cleaning'), _connector='AND'), _connector='OR'), null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
    ]