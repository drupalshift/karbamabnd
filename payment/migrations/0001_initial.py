# Generated by Django 2.0.2 on 2018-02-26 13:56

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.query_utils
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(blank=True, max_length=40, null=True, verbose_name='عنوان')),
                ('ref_num', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='شماره مرجع')),
                ('amount', models.IntegerField(blank=True, null=True, verbose_name='مفدار')),
                ('percent', models.IntegerField(blank=True, null=True, verbose_name='درصد')),
                ('max_amount', models.IntegerField(blank=True, null=True, verbose_name='حداکثر مقدار تخفیف')),
                ('expiration_date', models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضاء')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
            ],
            options={
                'verbose_name_plural': 'کوپن\u200cهای تخفیف',
                'verbose_name': 'کوپن تخفیف',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='شناسه شیء سرویس')),
                ('ref_num', models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره مرجع')),
                ('amount', models.FloatField(blank=True, null=True, verbose_name='مبلغ')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('content_type', models.ForeignKey(blank=True, limit_choices_to=django.db.models.query_utils.Q(django.db.models.query_utils.Q(('model', 'DryCleaning'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'CarpetCleaning'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'AC'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Medical'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Towing'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'HomeAppliance'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Plumbing'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Electricity'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Tuition'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Truck'), ('app_label', 'service_delivery'), _connector='AND'), django.db.models.query_utils.Q(('model', 'Cleaning'), ('app_label', 'service_delivery'), _connector='AND'), _connector='OR'), null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', verbose_name='نوع سرویس')),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.DiscountCoupon', verbose_name='تخفیف')),
            ],
            options={
                'verbose_name_plural': 'فاکتورها',
                'verbose_name': 'فاکتور',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('amount', models.FloatField(blank=True, null=True, verbose_name='مبلغ')),
                ('status', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'پرداخت نشده'), (2, 'در حال پرداخت'), (3, 'پرداخت شده')], default=1, null=True, verbose_name='وضعیت')),
                ('method', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'USSD'), (2, 'کارت بانکی'), (3, 'نقدی')], null=True, verbose_name='روش پرداخت')),
                ('card_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره کارت')),
                ('payment_code', models.IntegerField(blank=True, null=True, verbose_name='شماره پیگیری')),
                ('ref_num', models.CharField(blank=True, max_length=40, null=True, verbose_name='شماره مرجع')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.Invoice', verbose_name='فاکتور')),
            ],
            options={
                'verbose_name_plural': 'تراکنش\u200cهای پرداخت',
                'verbose_name': 'تراکنش پرداخت',
                'ordering': ('-created',),
            },
        ),
    ]