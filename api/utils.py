from .serializers import *


def active_services():
    return [service.content_type for service in ServiceDetail.objects.all().filter(is_active=True)]


def get_content_type_acronym(content_type):
    acronym = ''
    if content_type == 'ac':
        acronym = 'AC'
    elif content_type == 'carpetcleaning':
        acronym = 'CC'
    elif content_type == 'drycleaning':
        acronym = 'DC'
    elif content_type == 'medical':
        acronym = 'MD'
    elif content_type == 'homeappliance':
        acronym = 'HA'
    elif content_type == 'plumbing':
        acronym = 'PL'
    elif content_type == 'electricity':
        acronym = 'EL'
    elif content_type == 'tuition':
        acronym = 'TU'
    elif content_type == 'truck':
        acronym = 'TR'
    elif content_type == 'cleaning':
        acronym = 'CL'
    elif content_type == 'invoice':
        acronym = 'IV'
    elif content_type == 'discountcoupon':
        acronym = 'DS'
    elif content_type == 'paymenttransaction':
        acronym = 'PT'
    return acronym


def get_model_serializer(content_type, serializer_type=None):
    content_type = content_type.lower()
    serializer = False
    if content_type == 'ac':
        if serializer_type == 'create':
            serializer = ACCreateSerializer
        elif serializer_type == 'detail':
            serializer = ACDetailSerializer
        else:
            serializer = ACListSerializer
    elif content_type == 'drycleaning':
        if serializer_type == 'create':
            serializer = DryCleaningCreateSerializer
        elif serializer_type == 'detail':
            serializer = DryCleaningDetailSerializer
        else:
            serializer = DryCleaningListSerializer
    elif content_type == 'carpetcleaning':
        if serializer_type == 'create':
            serializer = CarpetCleaningCreateSerializer
        elif serializer_type == 'detail':
            serializer = CarpetCleaningDetailSerializer
        else:
            serializer = CarpetCleaningListSerializer
    elif content_type == 'medical':
        if serializer_type == 'create':
            serializer = MedicalCreateSerializer
        elif serializer_type == 'detail':
            serializer = MedicalDetailSerializer
        else:
            serializer = MedicalListSerializer
    elif content_type == 'homeappliance':
        if serializer_type == 'create':
            serializer = HomeApplianceCreateSerializer
        elif serializer_type == 'detail':
            serializer = HomeApplianceDetailSerializer
        else:
            serializer = HomeApplianceListSerializer
    elif content_type == 'plumbing':
        if serializer_type == 'create':
            serializer = PlumbingCreateSerializer
        elif serializer_type == 'detail':
            serializer = PlumbingDetailSerializer
        else:
            serializer = PlumbingListSerializer
    elif content_type == 'electricity':
        if serializer_type == 'create':
            serializer = ElectricityCreateSerializer
        elif serializer_type == 'detail':
            serializer = ElectricityDetailSerializer
        else:
            serializer = ElectricityListSerializer
    elif content_type == 'tuition':
        if serializer_type == 'create':
            serializer = TuitionCreateSerializer
        elif serializer_type == 'detail':
            serializer = TuitionCreateSerializer
        else:
            serializer = TuitionListSerializer
    elif content_type == 'truck':
        if serializer_type == 'create':
            serializer = TruckCreateSerializer
        elif serializer_type == 'detail':
            serializer = TruckDetailSerializer
        else:
            serializer = TruckListSerializer
    elif content_type == 'cleaning':
        if serializer_type == 'create':
            serializer = CleaningCreateSerializer
        elif serializer_type == 'detail':
            serializer = CleaningDetailSerializer
        else:
            serializer = CleaningListSerializer

    if not serializer:
        return None
    else:
        return serializer


def generate_ref_num(request, obj, model):
    ctype = ContentType.objects.get(model=model)
    ref_num = get_content_type_acronym(ctype.model) + str(obj.pk) + '-' +\
              jdatetime.datetime.now().strftime("%Y%m%d%H%M")
    if hasattr(obj, 'client'):
        obj.client = request.user
    obj.ref_num = ref_num
    obj.save()
    return
