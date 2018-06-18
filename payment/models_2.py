from django.db import models
from service_delivery.models import *
from django.conf import settings
from model_utils.models import TimeStampedModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Order(TimeStampedModel):
    personnel = models.ForeignKey(Personnel, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='پرسنل',
                                  related_name='personnel')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                               verbose_name='مشتری')
    ref_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره مرجع')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ('created',)

    def __str__(self):
        return self.ref_num


class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='سفارش')
    service_delivery_models = models.Q(app_label='service_delivery', model='DryCleaning') | \
                              models.Q(app_label='service_delivery', model='CarpetCleaning') | \
                              models.Q(app_label='service_delivery', model='AC') | \
                              models.Q(app_label='service_delivery', model='Medical') | \
                              models.Q(app_label='service_delivery', model='Towing') | \
                              models.Q(app_label='service_delivery', model='HomeAppliance') | \
                              models.Q(app_label='service_delivery', model='Plumbing') | \
                              models.Q(app_label='service_delivery', model='Electricity') | \
                              models.Q(app_label='service_delivery', model='Tuition') | \
                              models.Q(app_label='service_delivery', model='Truck') | \
                              models.Q(app_label='service_delivery', model='Cleaning')
    content_type = models.ForeignKey(ContentType, null=True, blank=True, limit_choices_to=service_delivery_models,
                                     on_delete=models.SET_NULL,
                                     verbose_name='نوع سرویس')
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='شناسه شیء سرویس')
    content_object = GenericForeignKey()

    class Meta:
        unique_together = ['content_type', 'object_id']
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return '{0}, {1]'.format(self.content_type, self.object_id)


class DiscountCoupon(TimeStampedModel):
    title = models.CharField(max_length=40, null=True, blank=True, verbose_name='عنوان')
    ref_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره مرجع')
    service = models.ForeignKey(ServiceDetail, null=True, blank=True, on_delete=models.SET_NULL,
                                verbose_name='نوع خدمت',
                                help_text='برای اعمال تخفیف به یک نوع سرویس، نوع آن را مشخص کنید.')
    amount = models.IntegerField(null=True, blank=True, verbose_name='مفدار')
    percent = models.IntegerField(null=True, blank=True, verbose_name='درصد')
    max_amount = models.IntegerField(null=True, blank=True, verbose_name='حداکثر مقدار تخفیف')
    expiration_date = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضاء')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'کوپن تخفیف'
        verbose_name_plural = 'کوپن‌های تخفیف'
        ordering = ('created',)

    def __str__(self):
        return '{0}, {1}'.format(self.title, self.ref_num)


class Invoice(TimeStampedModel):
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='سفارش')
    ref_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره مرجع')
    discount = models.ForeignKey(DiscountCoupon, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='تخفیف')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'فاکتور'
        verbose_name_plural = 'فاکتورها'
        ordering = ('created',)

    def __str__(self):
        return '{}'.format(self.ref_num)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='فاکتور')
    order_item = models.ForeignKey(OrderItem, null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name='آیتم سفارش')
    discount = models.ForeignKey(DiscountCoupon, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='تخفیف',
                                 help_text='اگر تخفیف برای آیتم فاکتور است در اینجا وارد می‌شود.')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'آیتم فاکتور'
        verbose_name_plural = 'آیتم‌های فاکتور'

    def __str__(self):
        return '{0}, {1}'.format(self.invoice.ref_num, self.order_item)


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
    amount = models.FloatField(null=True, blank=True, verbose_name='مقدار')
    Invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='فاکتور')
    status = models.IntegerField(null=True, blank=True, choices=STATUS_CHOICES, default=1, verbose_name='وضعیت')
    method = models.IntegerField(null=True, blank=True, choices=METHOD_CHOICES, verbose_name='روش پرداخت')
    card_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره کارت')
    payment_code = models.IntegerField(null=True, blank=True, verbose_name='شماره پیگیری')
    reference_code = models.IntegerField(null=True, blank=True, verbose_name='شماره مرجع')

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'تراکنش پرداخت'
        verbose_name_plural = 'تراکنش‌های پرداخت'
        ordering = ('created',)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.invoice, self.amount, self.status)

