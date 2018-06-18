from rest_framework import serializers
from payment.models import *
from service_delivery.models import *
from django.conf import settings
from star_ratings.models import Rating
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ('count', 'average')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'mobile', 'invite_id')


class PersonnelSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer()

    class Meta:
        model = Personnel
        fields = ('pk', 'first_name', 'last_name', 'mobile', 'ratings', 'type')


class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
    client = UserSerializer()
    personnel = PersonnelSerializer()
    content_type = serializers.ReadOnlyField(source='content_type.model')

    class Meta:
        model = Invoice
        fields = ('pk', 'ref_num', 'client', 'personnel', 'content_type', 'object_id', 'discount', 'description')


class ServiceDetailSerializer(serializers.HyperlinkedModelSerializer):
    content_type = serializers.ReadOnlyField(source='content_type.id')

    class Meta:
        model = ServiceDetail
        fields = ('pk', 'content_type', 'title', 'is_active', 'ban_item', 'price', 'position', 'active_days')


class ServiceBaseListSerializer(serializers.HyperlinkedModelSerializer):
    client = UserSerializer()
    personnel = PersonnelSerializer()
    used_discount = serializers.ReadOnlyField(source='used_discount.amount')

    class Meta:
        model = BaseService
        fields = ('pk', 'personnel', 'client', 'status', 'used_discount', 'ref_num', 'schedule_time', 'address',
                  'description', 'created', 'modified')
        # read_only_fields = ('id', 'created', 'modified','user',)
        # write_only_fields = ('client_time',)


class ServiceBaseCreateSerializer(serializers.HyperlinkedModelSerializer):
    used_discount = serializers.ReadOnlyField(source='used_discount.amount')

    class Meta:
        model = BaseService
        fields = ('pk', 'schedule_time', 'used_discount', 'city', 'address', 'description')


class UserOrderListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseService
        fields = ('pk', 'is_active', 'status', 'ref_num', 'schedule_time', 'address', 'description', 'created')


class AnnouncementListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Announcement
        fields = ('pk', 'title', 'city', 'is_active', 'is_ad', 'expiration_date')


class AnnouncementDetailSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Announcement
        fields = ('pk', 'title', 'city', 'is_active', 'is_ad', 'expiration_date', 'link', 'image')


# DryCleaning Serializer

class DryCleaningListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = DryCleaning
        fields = ServiceBaseListSerializer.Meta.fields + ('clothes', 'blanket', 'curtain', 'is_express',
                                                          'delivery_time')


class DryCleaningCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = DryCleaning
        fields = ServiceBaseCreateSerializer.Meta.fields + ('clothes', 'blanket', 'curtain', 'is_express',
                                                            'delivery_time')


class DryCleaningDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = DryCleaning
        fields = ServiceBaseCreateSerializer.Meta.fields + ('clothes', 'blanket', 'curtain', 'personnel', 'ref_num',
                                                            'status', 'is_express', 'delivery_time')


# CarpetCleaning Serializer

class CarpetCleaningItemSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CarpetCleaningItem
        fields = ('pk', 'type', 'size', 'carpet_type', 'created', 'modified')


class CarpetCleaningListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = CarpetCleaning
        fields = ServiceBaseListSerializer.Meta.fields + ('wash', 'stain', 'patch')


class CarpetCleaningCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = CarpetCleaning
        fields = ServiceBaseCreateSerializer.Meta.fields + ('wash', 'stain', 'patch')


class CarpetCleaningDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()
    items = CarpetCleaningItemSerializer(source='carpetcleaningitem_set', many=True)

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = CarpetCleaning
        fields = ServiceBaseCreateSerializer.Meta.fields + ('wash', 'stain', 'patch', 'items', 'personnel', 'ref_num',
                                                            'status')


# AC Serializer

class ACItemDetailSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ACItem
        fields = ('pk', 'ac_type', 'service_type', 'engine', 'brand', 'problem', 'created', 'modified')


class ACItemCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ACItem
        fields = ('ac_type', 'service_type', 'engine', 'brand', 'problem')


class ACListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = AC
        fields = ServiceBaseListSerializer.Meta.fields + ('split_install', 'split_repair', 'split_service',
                                                          'window_repair', 'window_service',)


class ACCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = AC
        fields = ServiceBaseCreateSerializer.Meta.fields + ('split_install', 'split_repair', 'split_service',
                                                            'window_repair', 'window_service',)


class ACDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()
    items = ACItemDetailSerializer(source='acitem_set', many=True)

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = AC
        fields = ServiceBaseCreateSerializer.Meta.fields + ('split_install', 'split_repair', 'split_service',
                                                            'window_repair', 'window_service', 'items', 'personnel',
                                                            'ref_num', 'status')


# Medical Serializer

class MedicalSessionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MedicalSession
        fields = ('pk', 'date', 'created', 'modified')


class MedicalListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = Medical
        fields = ServiceBaseListSerializer.Meta.fields + ('medic_gender', 'num_sessions')


class MedicalCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Medical
        fields = ServiceBaseCreateSerializer.Meta.fields + ('medic_gender', 'num_sessions')


class MedicalDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()
    sessions = MedicalSessionSerializer(source='medicalsession_set', many=True)

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Medical
        fields = ServiceBaseCreateSerializer.Meta.fields + ('medic_gender', 'num_sessions', 'sessions', 'personnel',
                                                            'ref_num', 'status')

# HomeAppliance Serializer


class HomeApplianceListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = HomeAppliance
        fields = ServiceBaseListSerializer.Meta.fields + ('brand', 'home_appliance_type', 'service_type', 'problem')


class HomeApplianceCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = HomeAppliance
        fields = ServiceBaseCreateSerializer.Meta.fields + ('brand', 'home_appliance_type', 'service_type', 'problem')


class HomeApplianceDetailSerializer(ServiceBaseCreateSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = HomeAppliance
        fields = ServiceBaseCreateSerializer.Meta.fields + ('brand', 'home_appliance_type', 'service_type', 'problem',
                                                            'personnel', 'ref_num', 'status')


# Plumbing Serializer

class PlumbingListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = Plumbing
        fields = ServiceBaseListSerializer.Meta.fields


class PlumbingCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Plumbing
        fields = ServiceBaseCreateSerializer.Meta.fields + ('water_and_sewage', 'water_heater', 'squat_toilet',
                                                            'flush_toilet', 'flushing_system', 'faucets',
                                                            'bathroom_sink', 'kitchen_sink', 'bath_tub', 'water_pump')


class PlumbingDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Plumbing
        fields = ServiceBaseCreateSerializer.Meta.fields + ('water_and_sewage', 'water_heater', 'squat_toilet',
                                                            'flush_toilet', 'flushing_system', 'faucets',
                                                            'bathroom_sink', 'kitchen_sink', 'bath_tub', 'water_pump',
                                                            'personnel', 'ref_num', 'status')


# Electric Serializer

class ElectricityListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = Electricity
        fields = ServiceBaseListSerializer.Meta.fields


class ElectricityCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Electricity
        fields = ServiceBaseCreateSerializer.Meta.fields + ('wiring', 'switch_and_socket', 'lighting', 'fuse_box',
                                                            'earth_wiring', 'phone_and_central_wiring', 'ventilation',
                                                            'ventilation_and_common_spaces', 'central_antenna',
                                                            'video_intercom',)


class ElectricityDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Electricity
        fields = ServiceBaseCreateSerializer.Meta.fields + ('wiring', 'switch_and_socket', 'lighting', 'fuse_box',
                                                            'earth_wiring', 'phone_and_central_wiring', 'ventilation',
                                                            'ventilation_and_common_spaces', 'central_antenna',
                                                            'video_intercom', 'personnel', 'ref_num', 'status')


# Tuition Serializer

class TuitionListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = Tuition
        fields = ServiceBaseListSerializer.Meta.fields + ('level', 'grade', 'lesson_name', 'tutor_gender',
                                                          'student_gender', 'num_sessions',)


class TuitionCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Tuition
        fields = ServiceBaseCreateSerializer.Meta.fields + ('level', 'grade', 'lesson_name', 'tutor_gender',
                                                            'student_gender', 'num_sessions')


class TuitionDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Tuition
        fields = ServiceBaseCreateSerializer.Meta.fields + ('level', 'grade', 'lesson_name', 'tutor_gender',
                                                            'student_gender', 'num_sessions', 'personnel', 'ref_num',
                                                            'status')


# Truck Serializer

class TruckListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = Truck
        fields = ServiceBaseListSerializer.Meta.fields + ('truck_type', 'num_worker')


class TruckCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Truck
        fields = ServiceBaseCreateSerializer.Meta.fields + ('truck_type', 'num_worker')


class TruckDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Truck
        fields = ServiceBaseCreateSerializer.Meta.fields + ('truck_type', 'num_worker', 'personnel', 'ref_num',
                                                            'status')


# Cleaning Serializer

class CleaningListSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseListSerializer.Meta):
        model = Cleaning
        fields = ServiceBaseListSerializer.Meta.fields + ('building_type', 'hour', 'male_worker_num',
                                                          'female_worker_num')


class CleaningCreateSerializer(ServiceBaseListSerializer):

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Cleaning
        fields = ServiceBaseCreateSerializer.Meta.fields + ('building_type', 'hour', 'male_worker_num',
                                                            'female_worker_num')


class CleaningDetailSerializer(ServiceBaseListSerializer):
    personnel = PersonnelSerializer()

    class Meta(ServiceBaseCreateSerializer.Meta):
        model = Cleaning
        fields = ServiceBaseCreateSerializer.Meta.fields + ('building_type', 'hour', 'male_worker_num',
                                                            'female_worker_num', 'personnel', 'ref_num', 'status')



