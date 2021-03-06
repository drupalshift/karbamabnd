# Generated by Django 2.0.2 on 2018-05-11 17:57

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('service_delivery', '0019_baseservice_created_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkRequestedNumbers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('mobile', models.CharField(max_length=14, unique=True, verbose_name='موبایل')),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name': 'شماره\u200c درخواست کننده',
                'verbose_name_plural': 'شماره\u200cهایی که درخواست لینک کردند',
            },
        ),
    ]
