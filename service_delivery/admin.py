from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from star_ratings.models import UserRating, Rating
from .models import *


from api.utils import active_services


# admin.site.unregister(Group)
# admin.site.unregister(Rating)
# admin.site.unregister(UserRating)

admin.ModelAdmin.list_per_page = 10


# @admin.register(LogEntry)
# class LogEntryAdmin(admin.ModelAdmin):
#     readonly_fields = ('user', 'object_id', 'content_type', 'action_time', 'object_repr', 'action_flag',
#                        'change_message')
#     list_display = ('user', 'object_id', 'content_type', 'action_time', 'object_repr', 'action_flag')
#     search_fields = ['object_id', 'user__username']
#     list_filter = ('content_type', 'action_flag')
#     date_hierarchy = 'action_time'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('invite_id',)
    list_display = ('username', 'city', 'mobile', 'mobile_verified', 'email')
    search_fields = ['username', 'mobile', 'email']
    list_filter = ('created', 'city', 'mobile_verified')


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    fields = (('type', 'city'), ('username', 'password'), ('first_name', 'last_name'), ('email', 'mobile'),
              ('ratings',),
              ('mobile_verified', 'email_verified', 'is_active', 'date_joined', 'description'))
    list_display = ('username', 'first_name', 'last_name', 'city', 'mobile', 'mobile_verified', '_jobs', 'ratings')
    search_fields = ['username', 'first_name', 'last_name', 'mobile', 'email']
    list_filter = ('type', 'city', 'created', 'is_active', 'mobile_verified')

    def _jobs(self, obj):
        job_count = 0
        for service_ctype in active_services():
            job_count += service_ctype.get_all_objects_for_this_type().filter(is_active=True, personnel=obj).count()
        return job_count

    _jobs.short_description = 'کارها'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'is_active', 'is_ad')
    fields = (('is_active', 'title', 'city', 'is_ad'),
              ('link', 'image'),
              ('expiration_date',))
    search_fields = ['title']
    list_filter = ('is_active', 'city', 'created')


@admin.register(ServiceDetail)
class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'is_active', 'position')
    search_fields = ['title']
    list_filter = ('is_active', 'city', 'created')


@admin.register(BaseService)
class BaseServiceAdmin(admin.ModelAdmin):
    raw_id_fields = ('client', 'personnel')
    readonly_fields = ('_ratings', 'ref_num', 'is_active', '_used_discount_amount', '_used_discount_percent',
                       'last_modified_moderator', '_client_number', '_personnel_number', 'created_time')
    fields = (('is_active', 'city', 'ref_num', '_ratings', 'status', '_used_discount_amount', '_used_discount_percent'),
              ('client', '_client_number', 'personnel', '_personnel_number'),
              ('schedule_time', 'address', 'created_time', 'description'),
              'last_modified_moderator')
    list_display = ('title', 'status', '_schedule_time', 'personnel', '_client_number', 'ref_num', '_created_time')
    search_fields = ['ref_num', 'client__mobile']
    list_filter = ('is_active', 'city', 'status', 'created')
    date_hierarchy = 'created'
    actions = ['set_state_approved', 'activate', 'deactivate']

    def save_model(self, request, obj, form, change):
        print(obj.schedule_time)
        print(type(obj.schedule_time))
        obj.last_modified_moderator = request.user
        super().save_model(request, obj, form, change)

    def set_state_approved(self, request, queryset):
        rows_updated = queryset.update(status=2)
        self.message_user(request, "%d سفارش با موفقیت به روز شد" % rows_updated)

    def deactivate(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, "%d سفارش با موفقیت به روز شد" % rows_updated)

    def activate(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, "%d سفارش با موفقیت به روز شد" % rows_updated)

    def _client_number(self, obj):
        return obj.client.mobile

    def _schedule_time(self, obj):
        return obj.schedule_time.strftime('%d %b %H:%M')

    def _created_time(self, obj):
        return obj.created_time.strftime('%d %b %H:%M')

    def _personnel_number(self, obj):
        return obj.personnel.mobile

    def _ratings(self, obj):
        rating = Rating.objects.for_instance(obj)
        return rating.average

    def _used_discount_amount(self, obj):
        return obj.used_discount.amount

    def _used_discount_percent(self, obj):
        return obj.used_discount.percent

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            kwargs["queryset"] = User.objects.all()  # restrict tu city adn active
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    _client_number.short_description = 'تلفن مشتری'
    _personnel_number.short_description = 'تلفن پرسنل'
    _schedule_time.short_description = 'زمان ارائه خدمت'
    _created_time.short_description = 'زمان ثبت سفارش'
    _schedule_time.admin_order_field = 'schedule_time'
    _created_time.admin_order_field = 'created_time'
    _ratings.short_description = 'امتیاز'
    _used_discount_amount.short_description = 'ملبغ تخفیف'
    _used_discount_percent.short_description = 'درصد تخفیف'
    _ratings.admin_order_field = 'ratings'
    activate.short_description = "فعال‌سازی سفارش‌های انتخاب شده"
    deactivate.short_description = "غیرفعال‌سازی سفارش‌های انتخاب شده"
    set_state_approved.short_description = "تأیید سفارش‌ها"


@admin.register(DryCleaning)
class DryCleaningAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('clothes', 'blanket', 'curtain', 'is_express', 'delivery_time'),)
    list_display = BaseServiceAdmin.list_display + ('is_express',)
    list_filter = BaseServiceAdmin.list_filter + ('is_express',)


class CarpetCleaningItemsInLine(admin.TabularInline):
    model = CarpetCleaningItem
    extra = 1


@admin.register(CarpetCleaning)
class CarpetCleaningAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('wash', 'stain', 'patch'),)
    list_display = BaseServiceAdmin.list_display + ('_carpetcleaningitems',)

    inlines = [
        CarpetCleaningItemsInLine
    ]

    def _carpetcleaningitems(self, obj):
        return obj.carpetcleaningitem_set.all().count()

    _carpetcleaningitems.short_description = 'تعداد آیتم‌ها'


class ACItemsInLine(admin.TabularInline):
    model = ACItem
    extra = 1


@admin.register(AC)
class ACAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('split_install', 'split_repair', 'split_service', 'window_repair',
                                         'window_service'),)
    list_display = BaseServiceAdmin.list_display + ('_acitems',)

    inlines = [
        ACItemsInLine
    ]

    def _acitems(self, obj):
        return obj.acitem_set.all().count()

    _acitems.short_description = 'تعداد آیتم‌ها'


class MedicalSessionInLine(admin.TabularInline):
    model = MedicalSession
    extra = 1


@admin.register(Medical)
class MedicalAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('num_sessions', 'medic_gender'),)
    list_display = BaseServiceAdmin.list_display + ('num_sessions', 'medic_gender', '_medicalitems',)
    list_filter = BaseServiceAdmin.list_filter + ('medic_gender',)

    inlines = [
        MedicalSessionInLine
    ]

    def _medicalitems(self, obj):
        return obj.medicalsession_set.all().count()

    _medicalitems.short_description = 'تعداد آیتم‌ها'


@admin.register(HomeAppliance)
class HomeApplianceAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('service_type', 'brand', 'home_appliance_type', 'problem'),)
    list_display = BaseServiceAdmin.list_display + ('service_type', 'brand', 'home_appliance_type',)
    list_filter = BaseServiceAdmin.list_filter + ('brand', 'home_appliance_type',)


@admin.register(Plumbing)
class PlumbingAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('water_and_sewage', 'water_heater', 'squat_toilet', 'flush_toilet',
                                         'flushing_system', 'faucets', 'bathroom_sink', 'kitchen_sink', 'bath_tub',
                                         'water_pump'),)


@admin.register(Electricity)
class ElectricityAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('wiring', 'switch_and_socket', 'lighting', 'fuse_box', 'earth_wiring',
                                         'phone_and_central_wiring',
               'ventilation', 'ventilation_and_common_spaces', 'central_antenna', 'video_intercom'),)


@admin.register(Tuition)
class TuitionAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('level', 'grade', 'lesson_name', 'tutor_gender', 'student_gender',
                                         'num_sessions'),)
    list_display = BaseServiceAdmin.list_display + ('level', 'lesson_name', 'tutor_gender', 'student_gender',)
    list_filter = BaseServiceAdmin.list_filter + ('level', 'grade', 'lesson_name', 'tutor_gender', 'student_gender',)


@admin.register(Truck)
class TruckAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('truck_type', 'num_worker'),)
    list_display = BaseServiceAdmin.list_display + ('truck_type', 'num_worker',)
    list_filter = BaseServiceAdmin.list_filter + ('truck_type',)


@admin.register(Cleaning)
class CleaningAdmin(BaseServiceAdmin):
    fields = BaseServiceAdmin.fields + (('building_type', 'hour', 'male_worker_num', 'female_worker_num'),)
    list_display = BaseServiceAdmin.list_display + ('building_type', 'hour',)
    list_filter = BaseServiceAdmin.list_filter + ('building_type',)


@admin.register(LinkRequestedNumbers)
class LinkRequestedNumbersAdmin(admin.ModelAdmin):
    readonly_fields = ('mobile',)
    fields = ('mobile',)
    list_display = ('mobile',)
    search_fields = ['mobile']
    date_hierarchy = 'created'

# TODO list_per_page default is 100. can set it to lower
