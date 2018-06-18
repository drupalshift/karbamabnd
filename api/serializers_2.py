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
        fields = ('pk', 'first_name', 'last_name', 'mobile', )


class PersonnelSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer()

    class Meta:
        model = Personnel
        fields = ('pk', 'first_name', 'last_name', 'mobile', 'ratings', 'type')


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    client = UserSerializer()
    personnel = PersonnelSerializer()
    content_type = serializers.ReadOnlyField(source='content_type.model')

    class Meta:
        model = Order
        fields = ('pk', 'ref_num', 'client', 'personnel', 'content_type', 'object_id')


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    client = UserSerializer()
    personnel = PersonnelSerializer()
    items = OrderItemsSerializer(source='orderitem_set', many=True)

    class Meta:
        model = Order
        fields = ('url', 'pk', 'ref_num', 'client', 'personnel', 'items')


class DryCleaningSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DryCleaning
        fields = ('url', 'pk', 'suit', 'shirt', 'manteau', 'blanket', 'curtain', 'status', 'created', 'modified',
                  'description')


class CarpetCleaningItemSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CarpetCleaningItem
        fields = ('url', 'pk', 'type', 'size', 'status', 'created', 'modified', 'description')


class CarpetCleaningSerializer(serializers.HyperlinkedModelSerializer):
    items = DryCleaningSerializer(source='drycleaningitem_set', many=True)

    class Meta:
        model = CarpetCleaning
        fields = ('url', 'pk', 'wash', 'stain', 'patch', 'items', 'status', 'created', 'modified', 'description')


class ACItemSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ACItem
        fields = ('url', 'pk', 'ac_type', 'service_type', 'status', 'created', 'modified', 'description')


class ACSerializer(serializers.HyperlinkedModelSerializer):
    items = ACItemSerializer(source='acitem_set', many=True)

    class Meta:
        model = AC
        fields = ('url', 'pk', 'wash', 'stain', 'patch', 'items', 'status', 'created', 'modified', 'description')


class MedicalSessionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MedicalSession
        fields = ('url', 'pk', 'date', 'status', 'created', 'modified', 'description')


class MedicalSerializer(serializers.HyperlinkedModelSerializer):
    sessions = MedicalSessionSerializer(source='medicalsession_set', many=True)

    class Meta:
        model = Medical
        fields = ('url', 'pk', 'medic_gender', 'num_sessions', 'sessions', 'status', 'created', 'modified',
                  'description')


class TowingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Towing
        fields = ('url', 'pk', 'type', 'status', 'created', 'modified', 'description')


class HomeApplianceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = HomeAppliance
        fields = ('url', 'pk', 'brand', 'home_appliance_type', 'service_type', 'status', 'created', 'modified',
                  'description')


class PlumbingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = HomeAppliance
        fields = ('url', 'pk', 'design_type', 'service_type', 'plumbing_type', 'status', 'created', 'modified',
                  'description')


class ElectricitySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Electricity
        fields = ('url', 'pk', 'service_type', 'electricity_type', 'design_type', 'status', 'created', 'modified',
                  'description')


class TuitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Tuition
        fields = ('url', 'pk', 'grade', 'lesson_name', 'tutor_gender', 'student_gender', 'num_sessions', 'status',
                  'created', 'modified', 'description')


class TruckSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Truck
        fields = ('url', 'pk', 'truck_type', 'num_worker', 'status', 'created', 'modified', 'description')


class CleaningSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Cleaning
        fields = ('url', 'pk', 'building_type', 'hour', 'gender', 'status', 'created', 'modified', 'description')


# TODO Build API


