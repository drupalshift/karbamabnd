from django.db import models
from django.contrib.auth.models import AbstractUser
from star_ratings.models import Rating
from django.contrib.contenttypes.fields import GenericRelation
from model_utils.models import TimeStampedModel
from .utils import send_ultrafast_sms
from multiselectfield import MultiSelectField
from django.contrib.contenttypes.models import ContentType
import jdatetime
from django_jalali.db import models as jmodels
from django_smalluuid.models import SmallUUIDField, uuid_default
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser, TimeStampedModel):
    CITY_CHOICES = (
        (1, 'بندرعباس'),
        (2, 'کرمان'),
        (3, 'یزد'),
    )

    city = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='شهر',
                                       choices=CITY_CHOICES)
    mobile = models.CharField(unique=True, max_length=14, null=True, blank=True, verbose_name='موبایل')
    mobile_verified = models.BooleanField(default=False, verbose_name='موبایل تأیید شده')
    email_verified = models.BooleanField(default=False, verbose_name='پست الکترونیکی تأیید شده')
    invitations_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد دعوت‌ها', default=0)
    used_invite_code = models.BooleanField(default=False, verbose_name='از کد دعوت کاربر دیگر استفاده کرده‌است')
    invite_id = SmallUUIDField(default=uuid_default(), null=True, blank=True, verbose_name='شناسه یکتا')

    MOBILE_FIELD = 'mobile'

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')


@receiver(post_save, sender=User)
def send_welcome_sms(sender, instance, created, **kwargs):
    if created:
        send_ultrafast_sms(mobile_num=instance.mobile, template_id=2178, Date=jdatetime.datetime.now().strftime('%d %b %Y'))


class Personnel(User):
    PERSONNEL_TYPE = (
        (1, 'خشک‌شویی'),
        (2, 'قالی‌شویی'),
        (3, 'کولر گازی'),
        (4, 'پزشکی'),
        (5, 'امداد خودرو - نیسان یدک‌کش'),
        (6, 'امداد خودرو - جرثقیل'),
        (7, 'لوازم خانگی'),
        (8, 'لوله‌کشی'),
        (9, 'برق‌کاری'),
        (10, 'تدریس'),
        (11, 'نظافت')
    )
    ratings = models.FloatField(default=0, null=True, blank=True, verbose_name='امتیاز')
    ratings_count = models.IntegerField(default=0, null=True, blank=True, verbose_name='تعداد امتیازات')
    type = models.PositiveSmallIntegerField(null=True, blank=True, choices=PERSONNEL_TYPE, verbose_name='نوع پرسنل')

    class Meta:
        verbose_name = 'پرسنل'
        verbose_name_plural = 'پرسنل'
        ordering = ('-created',)


class Announcement(TimeStampedModel):
    CITY_CHOICES = (
        (1, 'بندرعباس'),
        (2, 'کرمان'),
        (3, 'یزد'),
    )

    city = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='شهر', choices=CITY_CHOICES)
    title = models.CharField(max_length=80, null=True, blank=True, verbose_name='عنوان')
    is_ad = models.BooleanField(default=False, verbose_name='تبلیغ')
    link = models.CharField(max_length=80, null=True, blank=True, verbose_name='لینک')
    image = models.ImageField(max_length=80, null=True, blank=True, verbose_name='تصویر',
                              upload_to='static/uploads/images/announcements')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    expiration_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انقضاء')

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ('-created',)


class ServiceDetail(TimeStampedModel):
    DAYS_CHOICES = (
        (1, 'شنبه'),
        (2, 'یکشنبه'),
        (3, 'دوشنبه'),
        (4, 'سه‌شنبه'),
        (5, 'چهارشنبه'),
        (6, 'پنجشنبه'),
        (7, 'جمعه'),
    )
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
    CITY_CHOICES = (
        (1, 'بندرعباس'),
        (2, 'کرمان'),
        (3, 'یزد'),
    )

    city = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='شهر', choices=CITY_CHOICES)
    content_type = models.OneToOneField(ContentType, limit_choices_to=service_delivery_models, null=True, blank=True,
                                        on_delete=models.SET_NULL)
    title = models.CharField(max_length=40, unique=True, null=True, blank=True, verbose_name='عنوان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    price = models.TextField(null=True, blank=True, verbose_name='تعرفه')
    ban_item = models.TextField(null=True, blank=True, verbose_name='موارد غیر فعال')
    position = models.PositiveSmallIntegerField(unique=True, null=True, blank=True, verbose_name='جایگاه')
    active_days = models.TextField(null=True, blank=True, verbose_name='روزهای فعال',
                                   help_text="این خدمت در چه روزهایی از هفته"
                                             " فعال است؟ برای انتخاب همه"
                                             " روزهای هفته می‌توانید هیچکدام را انتخاب نکنید.")

    class Meta:
        verbose_name = 'جزئیات خدمت'
        verbose_name_plural = 'جزئیات خدمت‌ها'
        ordering = ('-created',)

    def __str__(self):
        return '{}'.format(self.title)


from payment.models import DiscountCoupon


def service_default_user():
    return User.objects.get(username='default').pk


def default_datetime():
    return jdatetime.datetime(1380, 8, 2, 12, 12, 12)


class BaseService(TimeStampedModel):
    STATUS_CHOICES = (
        (1, 'در حال بررسی'),
        (2, 'در حال انجام'),
        (3, 'خاتمه یافته'),
        (4, 'لفو شده توسط مشتری'),
        (5, 'لفو شده توسط سرویس‌دهنده'),
    )
    CITY_CHOICES = (
        (1, 'بندرعباس'),
        (2, 'کرمان'),
        (3, 'یزد'),
    )

    city = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='شهر', choices=CITY_CHOICES)
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    personnel = models.ForeignKey(Personnel, null=True, blank=True, verbose_name='پرسنل', related_name='personnel',
                                  on_delete=models.SET_NULL)
    client = models.ForeignKey(User, null=True, verbose_name='مشتری', on_delete=models.CASCADE)

    title = models.CharField(max_length=20, null=True, blank=True, verbose_name='عنوان')
    ref_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره پیگیری')
    status = models.PositiveSmallIntegerField(null=True, blank=True, choices=STATUS_CHOICES, verbose_name='وضعیت',
                                              default=1)
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    schedule_time = jmodels.jDateTimeField(verbose_name='زمان ارائه خدمت', default=default_datetime)
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='آدرس ارائه خدمت')
    ratings = GenericRelation(Rating, related_query_name='services', verbose_name='امتیاز')
    used_discount = models.ForeignKey(DiscountCoupon, null=True, blank=True, on_delete=models.SET_NULL,
                                      verbose_name='تخفیف')
    last_modified_moderator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                                verbose_name='ناظر آخرین تغییر', related_name='last_modified_moderator')
    created_time = jmodels.jDateTimeField(null=True, verbose_name='زمان ثبت سفارش')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.created_time:
            self.created_time = jdatetime.datetime.now()
        created_instance = self.pk  # is being created or not
        old_obj = None
        if created_instance:
            old_obj = BaseService.objects.get(pk=self.pk)
            if old_obj.status != self.status:
                if self.status in [1, 2] and not self.is_active:
                    self.is_active = True
                elif self.status in [3, 4, 5] and self.is_active:
                    self.is_active = False
            if old_obj.status and old_obj.status != 2 and self.status == 2:
                send_ultrafast_sms(mobile_num=self.client.mobile, template_id=2092,
                                   Day=self.schedule_time.strftime('%d %b %Y'),
                                   Hour=self.schedule_time.strftime('%H:%M'),
                                   Service=self._meta.verbose_name)
            elif old_obj.status and old_obj.status != 4 and self.status == 4:
                send_ultrafast_sms(mobile_num=self.client.mobile, template_id=2174, OrderType=self._meta.verbose_name)
            elif old_obj.status and old_obj.status != 3 and self.status == 3:
                send_ultrafast_sms(mobile_num=self.client.mobile, template_id=2172, OrderType=self._meta.verbose_name)
            elif old_obj.status and old_obj.status != 5 and self.status == 5:
                send_ultrafast_sms(mobile_num=self.client.mobile, template_id=2171, OrderType=self._meta.verbose_name)
            if old_obj and not old_obj.client and self.client:
                send_ultrafast_sms(mobile_num=self.client.mobile, template_id=2176, OrderType=self._meta.verbose_name)
        super().save()
        return


class DryCleaning(BaseService):
    is_express = models.BooleanField(blank=True, default=False, verbose_name='تحوبل اکسپرس')
    delivery_time = jmodels.jDateTimeField(null=True, blank=True, verbose_name='زمان تحویل')
    clothes = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='البسه')
    blanket = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='پتو')
    curtain = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='پرده')

    class Meta:
        verbose_name = 'خشکشویی'
        verbose_name_plural = 'خشکشویی‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'DC' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=DryCleaning)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class CarpetCleaning(BaseService):
    wash = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='شستشو')
    stain = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='لکه‌گیری')
    patch = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='رفوگری')

    class Meta:
        verbose_name = 'قالی‌شویی'
        verbose_name_plural = 'قالی‌شویی‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'CC' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=CarpetCleaning)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class CarpetCleaningItem(TimeStampedModel):
    CARPET_CLEANING_TYPE_CHOICES = (
        (1, 'شستشو'),
        (2, 'لکه‌گیری'),
        (3, 'رفوگری'),
    )
    SIZE_CHOICES = (
        (1, '۱ متری'),
        (2, '۲ متر'),
        (3, '۳ متری'),
        (4, '۶ متری'),
        (5, '۹ متری'),
        (6, '۱۲ متری'),
    )
    CARPET_TYPE_CHOICES = (
        (1, 'ماشینی'),
        (2, 'دستبافت'),
        (3, 'ابریشم'),
        (4, 'موکت'),
        (5, 'قالیچه'),
    )
    carpet_cleaning_obj = models.ForeignKey(CarpetCleaning, null=True, blank=True, on_delete=models.CASCADE,
                                            verbose_name='شیء قالی‌شویی')
    type = models.PositiveSmallIntegerField(null=True, blank=True, choices=CARPET_CLEANING_TYPE_CHOICES,
                                            verbose_name='نوع')
    size = models.PositiveSmallIntegerField(null=True, blank=True, choices=SIZE_CHOICES, verbose_name='اندازه')
    carpet_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=CARPET_TYPE_CHOICES,
                                                   verbose_name='نوع فرش')

    class Meta:
        verbose_name = 'آيتم قالی‌شویی'
        verbose_name_plural = 'آیتم‌های قالی‌شویی'
        ordering = ('-created',)


class AC(BaseService):
    split_install = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد نصب اسپلیت')
    split_repair = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد تعمیر اسپلیت')
    split_service = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد سرویس اسپلیت')
    window_repair = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد تعمیر پنجره‌ای')
    window_service = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد سرویس پنجره‌ای')

    class Meta:
        verbose_name = 'کولر گازی'
        verbose_name_plural = 'کولر گازی‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'AC' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=AC)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class ACItem(TimeStampedModel):
    AC_TYPE_CHOICES = (
        (1, 'اسپلیت'),
        (2, 'پنجره‌ای'),
    )
    SERVICE_TYPE_CHOICES = (
        (1, 'نصب و راه‌اندازی'),
        (2, 'تعمیر'),
        (3, 'سرویس'),
    )
    ENGINE_TYPE_CHOICES = (
        (1, 12000),
        (2, 18000),
        (3, 24000),
        (4, 30000),
        (5, 36000),
        (6, 42000),
        (7, 48000),
        (8, 60000),
        (9, 90000),
    )
    BRANDS_CHOICES = (
        (1, 'سامسونگ'),
        (2, 'ال‌جی'),
        (3, 'بوش'),
        (4, 'جنرال'),
        (5, 'پاناسونیک'),
        (6, 'گری'),
        (7, 'میدیا'),
        (8, 'هایس'),
        (9, 'توشیبا'),
        (10, 'تراست'),
        (11, 'میتوشی'),
        (12, 'هیتاچی'),
        (13, 'سایر'),
    )
    PROBLEM_CHOICES = (
        (1, 'دستگاه روشن نمی‌شود'),
        (2, 'خوب سرد نمی‌کند'),
        (3, 'روی موتور نمی‌رود'),
        (4, 'لرزش غیر‌عادی'),
        (5, 'کولر یخ می‌زند'),
        (6, 'هنگام روشن شدن فیوز می‌پراند'),
        (7, 'ریموت کار نمی‌کند'),
        (8, 'بدنه کولر برق دارد'),
        (9, 'متناوباً خاموش و روشن می‌شود'),
        (10, 'سایر'),
    )
    ac_obj = models.ForeignKey(AC, null=True, blank=True, on_delete=models.CASCADE, verbose_name='شیء کولر گازی')
    ac_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=AC_TYPE_CHOICES,
                                               verbose_name='نوع کولر گازی')
    service_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=SERVICE_TYPE_CHOICES,
                                                    verbose_name='نوع سرویس')
    engine = models.PositiveSmallIntegerField(null=True, blank=True, choices=ENGINE_TYPE_CHOICES,  verbose_name='موتور')
    brand = models.PositiveSmallIntegerField(null=True, blank=True, choices=BRANDS_CHOICES, verbose_name='برند')
    problem = models.PositiveSmallIntegerField(null=True, blank=True, choices=PROBLEM_CHOICES,
                                               verbose_name='علائم خرابی')

    class Meta:
        verbose_name = 'آیتم کولر گازی'
        verbose_name_plural = 'آیتم‌های کولر گازی‌ها'
        ordering = ('-created',)


class Medical(BaseService):
    GENDER_CHOICES = (
        (1, 'مرد'),
        (2, 'زن'),
    )
    medic_gender = models.PositiveSmallIntegerField(null=True, blank=True, choices=GENDER_CHOICES,
                                                    verbose_name='جنسیت پزشک')
    num_sessions = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد جلسات')

    class Meta:
        verbose_name = 'پزشکی'
        verbose_name_plural = 'پزشکی‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'MD' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=Medical)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class MedicalSession(TimeStampedModel):
    medical_obj = models.ForeignKey(Medical, null=True, blank=True, on_delete=models.CASCADE, verbose_name='شیء پزشکی')
    date = jmodels.jDateTimeField(null=True, blank=True, verbose_name='تاریخ جلسه')

    class Meta:
        verbose_name = 'وقت پزشکی'
        verbose_name_plural = 'وقت‌های پزشکی'
        ordering = ('-created',)


class HomeAppliance(BaseService):
    SERVICE_TYPE_CHOICES = (
        (1, 'نصب و راه‌اندازی'),
        (2, 'تعمیر'),
        (3, 'سرویس ساید بای ساید'),
    )
    BRANDS_CHOICES = (
        (1, 'سامسونگ'),
        (2, 'ال‌جی'),
        (3, 'بوش'),
        (4, 'امرسان'),
        (5, 'اسنوا'),
        (6, 'سینجر'),
        (7, 'میدیا'),
        (8, 'دوو'),
        (9, 'لکو'),
        (10, 'پاناسونیک'),
        (11, 'جنرال الکتریک'),
        (12, 'الکترواستیل'),
        (13, 'AEG'),
        (14, 'کنوود'),
        (15, 'هارداستون'),
        (16, 'فیلور'),
        (17, 'هایر'),
        (18, 'هیمالیا'),
        (19, 'بیمکث'),
        (20, 'استیل البرز'),
        (21, 'اخوان'),
        (22, 'داتیس'),
        (23, 'پیلوت'),
        (24, 'پارس خزر'),
        (25, 'هیتاچی'),
        (26, 'فیلیپس'),
        (27, 'زیمنس'),
        (28, 'آبسال'),
        (29, 'سونی'),
        (30, 'سایر'),
    )
    HOME_APPLIANCE_TYPE_CHOICES = (
        (1, 'یخچال'),
        (2, 'جاروبرقی'),
        (3, 'ماشین لباس‌شویی'),
        (4, 'ماشین ظرف‌شویی'),
        (5, 'اجاق‌گاز'),
        (6, 'هود'),
    )
    PROBLEM_CHOICES = (
        (0, 'هیچکدام'),
        (1, 'دستگاه روشن نمی شود'),
        (2, 'یخچال خنک نمی کند'),
        (3, 'برفک می زند'),
        (4, 'صدای غیر عادی می دهد'),
        (5, 'موتور خاموش و روشن می شود'),
        (6, 'بدنه دستگاه برق دارد'),
        (7, 'درب بسته نمی شود'),
        (8, 'یخ ساز کار نمی کند'),
        (9, 'فریزر منجمد نمی کند'),
        (10, 'کلیدها کار نمی کند'),
        (11, 'مکش هود ضعیف است'),
        (12, 'سنسور بو یا دما کار نمی کند'),
        (13, 'هود لرزش غیرعادی دارد'),
        (14, 'هود صدای غیرعادی دارد'),
        (15, 'بعضی یا همه شعله ها روشن نمی شود'),
        (16, 'فندک اجاق گاز کار نمی کند'),
        (17, 'ترموکوپل اجاق گاز کار نمی کند'),
        (18, 'دستگاه مکش قوی ندارد'),
        (19, 'کارکردن با بو یا دود سوختگی'),
        (20, 'روشن می شود اما کار نمی کند'),
        (21, 'درب بسته نمی شود'),
        (22, 'اثر مواد شوینده روی لباس می  ماند'),
        (23, 'عدم تخلیه آب'),
        (24, 'دستگاه هنگام کار بوی سوختگی می دهد'),
        (25, 'لرزش غیرعادی دارد'),
        (26, 'درب باز یا بسته نمی شود'),
        (27, 'خشک کن کار نمی کند'),
        (28, 'آب گرم نمی کند'),
        (29, 'درب آب می دهد'),
        (30, 'کلیدها کار نمی کند'),
        (31, 'اتومات دستگاه کار نمی کند'),
        (32, 'ظرف ها خوب شسته نمی شوند'),
        (33, 'عدم تخلیه آب'),
        (34, 'سایر'),
    )
    service_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=SERVICE_TYPE_CHOICES,
                                                    verbose_name='نوع سرویس')
    brand = models.PositiveSmallIntegerField(null=True, blank=True, choices=BRANDS_CHOICES, verbose_name='برند')
    home_appliance_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=HOME_APPLIANCE_TYPE_CHOICES,
                                                           verbose_name='نوع لوازم خانگی')
    problem = models.PositiveSmallIntegerField(null=True, blank=True, choices=PROBLEM_CHOICES,
                                               verbose_name='علائم خرابی')

    class Meta:
        verbose_name = 'لوازم خانگی'
        verbose_name_plural = 'لوازم خانگی'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.problem == 0:
            self.problem = None
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'HA' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=HomeAppliance)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class Plumbing(BaseService):
    SERVICE_TYPE_CHOICES = (
        (1, 'نصب'),
        (2, 'تعمیر'),
    )
    WATER_AND_SEWAGE_CHOICES = (
        (1, 'نصب روکار'),
        (2, 'نصب توکار'),
        (3, 'رفع ترکیدگی روکار'),
        (4, 'رفع ترکیدگی توکار'),
    )

    water_and_sewage = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='آب و فاضلاب',
                                                        choices=WATER_AND_SEWAGE_CHOICES)
    water_heater = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='آبگرمکن',
                                                    choices=SERVICE_TYPE_CHOICES)
    squat_toilet = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='توالت ایرانی',
                                                    choices=SERVICE_TYPE_CHOICES)
    flush_toilet = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='توالت فرنگی',
                                                    choices=SERVICE_TYPE_CHOICES)
    flushing_system = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='فلاش تانک',
                                                       choices=SERVICE_TYPE_CHOICES)
    faucets = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='شیر‌آلات',
                                               choices=SERVICE_TYPE_CHOICES)
    bathroom_sink = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='روشویی',
                                                     choices=SERVICE_TYPE_CHOICES)
    kitchen_sink = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='سینک ظرقشویی',
                                                    choices=SERVICE_TYPE_CHOICES)
    bath_tub = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='وان حمام',
                                                choices=SERVICE_TYPE_CHOICES)
    water_pump = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='پمپ آب',
                                                  choices=SERVICE_TYPE_CHOICES)

    class Meta:
        verbose_name = 'لوله‌کشی'
        verbose_name_plural = 'لوله‌کشی‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'PL' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=Plumbing)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class Electricity(BaseService):
    SERVICE_TYPE_CHOICES_1 = (
        (1, 'نصب'),
        (2, 'رفع عیب'),
    )
    SERVICE_TYPE_CHOICES_2 = (
        (1, 'نصب'),
        (2, 'رفع عیب'),
        (3, 'طراحی'),
    )
    WIRING_CHOICES = (
        (1, 'روکار'),
        (2, 'توکار'),
    )
    LIGHTING_CHOICES = (
        (1, 'نصب و تعویض لوستر'),
        (2, 'اجرای نور مخفی'),
        (3, 'نصب و تعویض چراغ'),
    )
    PHONE_AND_CENTRAL_CHOICES = (
        (1, 'سیم‌کشی جدید'),
        (2, 'رفع عیب'),
        (3, 'خدمات سانترال'),
    )
    wiring = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='سیم‌کشی',
                                              choices=WIRING_CHOICES)
    switch_and_socket = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='کلید و پریز',
                                                         choices=WIRING_CHOICES)
    lighting = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='روشنایی',
                                                choices=LIGHTING_CHOICES)
    fuse_box = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='جعبه فیوز',
                                                choices=SERVICE_TYPE_CHOICES_1)
    earth_wiring = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='سیم‌کشی ارث',
                                                    choices=SERVICE_TYPE_CHOICES_1)
    phone_and_central_wiring = models.PositiveSmallIntegerField(null=True, blank=True,
                                                                verbose_name='سیم‌کشی تلفن و سانترال',
                                                                choices=PHONE_AND_CENTRAL_CHOICES)
    ventilation = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='هواکش',
                                                   choices=SERVICE_TYPE_CHOICES_1)
    ventilation_and_common_spaces = models.PositiveSmallIntegerField(null=True, blank=True,
                                                                     verbose_name='هواکش و مشاعات',
                                                                     choices=SERVICE_TYPE_CHOICES_2)
    central_antenna = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='آنتن مرکزی',
                                                       choices=SERVICE_TYPE_CHOICES_1)
    video_intercom = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='آیفون تصویری',
                                                      choices=SERVICE_TYPE_CHOICES_1)

    class Meta:
        verbose_name = 'برق‌کاری'
        verbose_name_plural = 'برق‌کاری‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'EL' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=Electricity)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class Tuition(BaseService):
    LEVEL_CHOICES = (
        (1, 'ابتدایی'),
        (2, 'متوسطه دوم (علوم تجربی)'),
        (3, 'متوسطه دوم (ریاضی فیزیک)'),
        (4, 'متوسطه'),
        (5, 'تیزهوشان'),
    )
    GRADE_CHOICES = (
        (1, 'سال اول'),
        (2, 'سال دوم'),
        (3, 'سال سوم'),
        (4, 'سال چهارم'),
        (5, 'سال پنجم'),
        (6, 'سال ششم'),
        (7, 'سال هفتم'),
        (8, 'سال هشتم'),
        (9, 'سال نهم'),
        (10, 'سال دهم'),
        (11, 'سال یازدهم'),
        (12, 'سال دوازدهم'),
        (13, 'ششم به هفتم'),
        (14, 'نهم به دهم'),
    )
    LESSON_NAME_CHOICES = (
        (1, 'ریاضی'),
        (2, 'علوم تجربی'),
        (3, 'فارسی'),
        (4, 'نگارش'),
        (5, 'عربی'),
        (6, 'زبان انگلیسی'),
        (7, 'زیست‌شناسی'),
        (8, 'فیزیک'),
        (9, 'شیمی'),
        (10, 'حسابان'),
        (11, 'هندسه'),
        (12, 'آمار و احتمالات'),
        (13, 'ریاضات گسسته'),
        (14, 'استعداد تحصیلی'),
        (15, 'زمین‌شناسی'),
        (16, 'ادبیات'),

    )
    TUTOR_GENDER_CHOICES = (
        (1, 'مرد'),
        (2, 'زن'),
        (3, 'فرقی نمی‌کند'),
    )
    STUDENT_GENDER_CHOICES = (
        (1, 'پسر'),
        (2, 'دختر'),
    )
    level = models.PositiveSmallIntegerField(null=True, blank=True, choices=LEVEL_CHOICES, verbose_name='مقطع تحصیلی')
    grade = models.PositiveSmallIntegerField(null=True, blank=True, choices=GRADE_CHOICES, verbose_name='پایه تحصیلی')
    lesson_name = models.PositiveSmallIntegerField(null=True, blank=True, choices=LESSON_NAME_CHOICES,
                                                   verbose_name='اسم درس')
    tutor_gender = models.PositiveSmallIntegerField(null=True, blank=True, choices=TUTOR_GENDER_CHOICES,
                                                    verbose_name='جنسیت استاد')
    student_gender = models.PositiveSmallIntegerField(null=True, blank=True, choices=STUDENT_GENDER_CHOICES,
                                                      verbose_name='جنسیت دانش‌آموز')
    num_sessions = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد جلسات')

    class Meta:
        verbose_name = 'تدریس'
        verbose_name_plural = 'تدریس‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'TU' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=Tuition)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class Truck(BaseService):
    TRUCK_TYPE_CHOICES = (
        (1, 'وانت‌بار'),
        (2, 'نیسان‌بار'),
        (3, 'کامبونت سر باز'),
        (4, 'کامیونت چادری'),
    )
    truck_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=TRUCK_TYPE_CHOICES,
                                                  verbose_name='نوع اتوبار')
    num_worker = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد کارگران')

    class Meta:
        verbose_name = 'اتوبار'
        verbose_name_plural = 'اتوبارها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'TR' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=Truck)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class Cleaning(BaseService):
    BUILDING_TYPE_CHOICES = (
        (1, 'منزل'),
        (2, 'اداری تجاری'),
        (3, 'مشاعات'),
    )
    building_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=BUILDING_TYPE_CHOICES,
                                                     verbose_name='نوع مکان')
    hour = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='مقدار ساعت')
    male_worker_num = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد نیروی مرد')
    female_worker_num = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='تعداد نیروی زن')

    class Meta:
        verbose_name = 'نظافت'
        verbose_name_plural = 'نظافت‌ها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'CL' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


@receiver(post_save, sender=Cleaning)
def send_new_order_sms(sender, instance, created, **kwargs):
    if created:
        if not instance.client:
            return
        else:
            send_ultrafast_sms(mobile_num=instance.client.mobile, template_id=2176,
                               OrderType=instance._meta.verbose_name)


class Towing(BaseService):

    class Meta:
        verbose_name = 'امداد خودرو'
        verbose_name_plural = 'امداد خودروها'
        ordering = ('-created',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        if not self.ref_num:
            self.title = self._meta.verbose_name
            self.ref_num = 'TW' + str(self.pk) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M")
            self.save()
            return
        else:
            return


class LinkRequestedNumbers(TimeStampedModel):
    mobile = models.CharField(unique=True, max_length=14, verbose_name='موبایل')

    class Meta:
        verbose_name = 'شماره‌ درخواست کننده'
        verbose_name_plural = 'شماره‌هایی که درخواست لینک کردند'
        ordering = ('-created',)
