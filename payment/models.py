from django.db import models
from service_delivery.models import *
from model_utils.models import TimeStampedModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class DiscountCoupon(TimeStampedModel):
    title = models.CharField(max_length=40, null=True, blank=True, verbose_name='عنوان')
    ref_num = models.CharField(max_length=20, null=True, blank=True, unique=True, verbose_name='شماره مرجع',
                               help_text='کد در نظر گرفته شده برای تخفیف را وارد نمایید')
    service = models.ForeignKey(ServiceDetail, null=True, blank=True, on_delete=models.SET_NULL,
                                verbose_name='نوع خدمت',
                                help_text='برای اعمال تخفیف به یک نوع سرویس، نوع آن را مشخص کنید.')
    single_user = models.BooleanField(default=False, verbose_name='تک کاربر')
    amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='مبلغ')
    percent = models.PositiveIntegerField(null=True, blank=True, verbose_name='درصد',
                                          help_text='تخفیف درصدی در صورتی اعمال می‌شود که مبلغ را مشخص نکنید.')
    max_discount_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر مقدار تخفیف')
    min_invoice_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداقل مبلغ فاکتور')
    expiration_date = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضاء')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'کوپن تخفیف'
        verbose_name_plural = 'کوپن‌های تخفیف'
        ordering = ('-created',)

    def __str__(self):
        return '{0}, {1}'.format(self.title, self.ref_num)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        if not self.ref_num:
            self.ref_num = 'DS' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


class UsedDiscounts(TimeStampedModel):
    discount_coupon = models.ForeignKey(DiscountCoupon, null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name='کوپن تخفیف')
    client = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='مشتری')

    class Meta:
        verbose_name = 'کوپن تخفیف استفاده شده'
        verbose_name_plural = 'کوپن‌های تخفیف استفاده شده'
        ordering = ('-created',)


class Invoice(TimeStampedModel):
    service_delivery_models = models.Q(app_label='service_delivery', model='DryCleaning') | \
                              models.Q(app_label='service_delivery', model='CarpetCleaning') | \
                              models.Q(app_label='service_delivery', model='AC') | \
                              models.Q(app_label='service_delivery', model='Medical') | \
                              models.Q(app_label='service_delivery', model='HomeAppliance') | \
                              models.Q(app_label='service_delivery', model='Plumbing') | \
                              models.Q(app_label='service_delivery', model='Electricity') | \
                              models.Q(app_label='service_delivery', model='Tuition') | \
                              models.Q(app_label='service_delivery', model='Truck') | \
                              models.Q(app_label='service_delivery', model='Cleaning')
    content_type = models.ForeignKey(ContentType, limit_choices_to=service_delivery_models, null=True, blank=True,
                                     on_delete=models.SET_NULL, verbose_name='نوع سرویس')
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='شناسه شیء سرویس')
    content_object = GenericForeignKey('content_type', 'object_id')
    ref_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره مرجع')
    discount = models.ForeignKey(DiscountCoupon, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='تخفیف')
    amount = models.FloatField(null=True, blank=True, verbose_name='مبلغ')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'فاکتور'
        verbose_name_plural = 'فاکتورها'
        ordering = ('-created',)

    def __str__(self):
        return '{}'.format(self.ref_num)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        if not self.ref_num:
            self.ref_num = 'IV' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


class PaymentTransaction(TimeStampedModel):
    METHOD_CHOICES = (
        (1, 'USSD'),
        (2, 'کارت بانکی'),
        (3, 'نقدی'),
    )
    STATUS_CHOICES = (
        (1, 'پرداخت نشده'),
        (2, 'در حال پرداخت'),
        (3, 'پرداخت شده'),
    )
    amount = models.FloatField(null=True, blank=True, verbose_name='مبلغ')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='فاکتور')
    status = models.PositiveSmallIntegerField(null=True, blank=True, choices=STATUS_CHOICES, default=1, verbose_name='وضعیت')
    method = models.PositiveSmallIntegerField(null=True, blank=True, choices=METHOD_CHOICES, verbose_name='روش پرداخت')
    card_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره کارت')
    payment_code = models.PositiveIntegerField(null=True, blank=True, verbose_name='شماره پیگیری')
    ref_num = models.CharField(max_length=40, null=True, blank=True, verbose_name='شماره مرجع')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'تراکنش پرداخت'
        verbose_name_plural = 'تراکنش‌های پرداخت'
        ordering = ('-created',)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.invoice, self.amount, self.status)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        if not self.ref_num:
            self.ref_num = 'PT' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return

