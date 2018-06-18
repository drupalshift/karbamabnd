from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from drf_multiple_model.views import ObjectMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from rest_framework.pagination import LimitOffsetPagination
from .serializers import *
from star_ratings.models import UserRating
from .utils import active_services
from service_delivery.utils import send_ultrafast_sms
from drfpasswordless.tasks import refresh_sms_token
from django.shortcuts import redirect
from rest_framework import viewsets, filters
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
import json
from constance import config
import sendgrid
from sendgrid.helpers.mail import *
import re
import uuid
from os.path import join


@require_http_methods(["GET"])
def serve_enamad_confirmation(request):
    print(join(settings.BASE_DIR, 'static/390083.txt'))
    content = open(join(settings.BASE_DIR, 'static/390083.txt'), "rb").read()
    return HttpResponse(content, content_type='text/plain')


@require_http_methods(["GET"])
def order_details_view(request):
    if 'content_type' not in request.GET or 'object_id' not in request.GET:
        return JsonResponse(data={'error': 'content_type/object_id invalid'}, status=400)
    try:
        content_type = ContentType.objects.get(app_label='service_delivery', model=request.GET['content_type'])
        order = content_type.get_object_for_this_type(pk=request.GET['object_id'])
    except Exception as e:
        return JsonResponse(data={'error': e, 'message': 'content_type/object not found'}, status=404)
    serialized_order = None
    if order.client == request.user:
        if content_type.model == 'ac':
            serialized_order = ACDetailSerializer(order)
        elif content_type.model == 'drycleaning':
            serialized_order = DryCleaningDetailSerializer(order)
        elif content_type.model == 'carpetcleaning':
            serialized_order = CarpetCleaningDetailSerializer(order)
        elif content_type.model == 'medical':
            serialized_order = MedicalDetailSerializer(order)
        elif content_type.model == 'homeappliance':
            serialized_order = HomeApplianceDetailSerializer(order)
        elif content_type.model == 'plumbing':
            serialized_order = PlumbingDetailSerializer(order)
        elif content_type.model == 'electricity':
            serialized_order = ElectricityDetailSerializer(order)
        elif content_type.model == 'tuition':
            serialized_order = TuitionDetailSerializer(order)
        elif content_type.model == 'truck':
            serialized_order = TruckDetailSerializer(order)
        elif content_type.model == 'cleaning':
            serialized_order = CleaningDetailSerializer(order)

        if serialized_order:
            return JsonResponse(data=serialized_order.data, status=200)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'message': 'شما اجازه دسترسی به این منبع را ندارید'}, status=403)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_support_number(request):
    return Response(data={'support_number': config.SUPPORT_NUMBER}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_app_version(request):
    return Response(data={'app_version': config.APP_VERSION}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_express_delivery_constant(request):
    return Response(data={'express_delivery_constant/': config.EXPRESS_DELIVERY_CONSTANT}, status=status.HTTP_200_OK)


def get_latest_orders_ajax(request):
    orders = []
    data = []
    for service_ctype in active_services():
        ctype_orders = service_ctype.get_all_objects_for_this_type().filter(is_active=True).order_by('-created')[:10]
        for order in ctype_orders:
            orders.append(order)
    for order in orders:
        data.append(
            {
                'pk': order.pk,
                'model': order.__class__.__name__.lower(),
                'status': order.status,
                'ref_num': order.ref_num
            }
        )

    return HttpResponse(json.dumps(data), content_type='application/json', status=status.HTTP_200_OK)


class TowingView(generics.ListAPIView):
    queryset = Personnel.objects.filter(type__in=[5, 6]).order_by('-created')
    serializer_class = PersonnelSerializer

    def get_queryset(self):
        queryset = Personnel.objects.filter(type__in=[5, 6], city=self.request.query_params.get('city')) \
            .order_by('-created')
        return queryset


class BaseServiceView(generics.ListAPIView):
    queryset = BaseService.objects.all().order_by('-created')
    serializer_class = ServiceBaseListSerializer

    def get_queryset(self):
        queryset = BaseService.objects.filter(client=self.request.user).order_by('-created')
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 10


class UserOrderList(ObjectMultipleModelAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPagination

    querylist = []

    # for service_ctype in active_services():
    #     querylist.append({'queryset': service_ctype.get_all_objects_for_this_type().order_by('-created'),
    #                      'serializer_class': UserOrderListSerializer})

    def get_querylist(self):
        querylist = []
        services = active_services()
        for service_ctype in services:
            querylist.append({'queryset': service_ctype.get_all_objects_for_this_type().order_by('-created'),
                              'serializer_class': UserOrderListSerializer})

        return querylist

    def list(self, request, *args, **kwargs):
        querylist = self.get_querylist()

        for item in querylist:
            item['queryset'] = item['queryset'].filter(client=self.request.user)

            is_active = self.request.query_params.get('is_active', None)
            if is_active is not None:
                item['queryset'] = item['queryset'].filter(is_active=is_active)

        results = self.get_empty_results()

        for query_data in querylist:
            self.check_query_data(query_data)

            queryset = self.load_queryset(query_data, request, *args, **kwargs)

            if not queryset:
                continue

            # Run the paired serializer
            context = self.get_serializer_context()
            data = query_data['serializer_class'](queryset, many=True, context=context).data

            label = self.get_label(queryset, query_data)

            # Add the serializer data to the running results tally
            results = self.add_to_results(data, label, results)

        formatted_results = self.format_results(results, request)

        if self.is_paginated:
            try:
                formatted_results = self.paginator.format_response(formatted_results)
            except AttributeError:
                raise NotImplementedError("".format(self.__class__.__name__))

        return Response(formatted_results)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def use_discount_view(request):
    obj = None
    try:
        content_type = ContentType.objects.get(app_label='service_delivery', model=request.data['content_type'])
        service_details = ServiceDetail.objects.get(content_type=content_type)
        coupon = DiscountCoupon.objects.get(ref_num=request.data['coupon'])
        if 'object_id' in request.data:
            obj = content_type.get_object_for_this_type(pk=int(request.data['object_id']))
    except Exception as e:
        return Response(data={'error': e}, status=status.HTTP_400_BAD_REQUEST)

    coupon_is_valid = True
    discount_message = ''
    if coupon.service and coupon.service != service_details:
        coupon_is_valid = False
        discount_message = 'این تخفیف برای این نوع خدمت نیست'
    elif datetime.now() > coupon.expiration_date:
        coupon_is_valid = False  # celery check active discounts for expiration date and deactive them
        discount_message = 'این کوپن منقضی شده است'
    elif not coupon.is_active:
        coupon_is_valid = False
        discount_message = 'این کوپن استفاده شده است'

    if not coupon_is_valid:
        return Response(data={'message': discount_message}, status=status.HTTP_403_FORBIDDEN)

    coupon_used = UsedDiscounts.objects.filter(client=request.user, discount_coupon=coupon)
    if coupon_used:
        discount_message = 'شما قبلاً از این کوپن استفاده کرده‌اید'
        return Response(data={'message': discount_message}, status=status.HTTP_403_FORBIDDEN)

    if obj:
        if obj.used_discount:
            discount_message = 'شما قبلاً برای این سفارش از تخفیف استفاده کرده‌اید'
            return Response(data={'message': discount_message}, status=status.HTTP_403_FORBIDDEN)
        else:
            used_coupon = UsedDiscounts.objects.create(discount_coupon=coupon, client=request.user)
            used_coupon.save()
            if coupon.single_user:
                coupon.is_active = False
                coupon.save()
            obj.used_discount = coupon
            obj.save()
            data = {'amount': coupon.amount,
                    'percent': coupon.percent,
                    'max_amount': coupon.max_discount_amount,
                    'message': 'تخفیف اعمال شد'}

    else:
        data = {'amount': coupon.amount,
                'percent': coupon.percent,
                'max_amount': coupon.max_discount_amount}

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def user_invite_view(request):
    # invite_id = request.POST.get('invite_id')
    invite_id = request.data['invite_id']

    if invite_id == str(request.user.invite_id):
        return Response(data={'error': 'نمی‌توانید خود را دعوت کنید!'}, status=status.HTTP_403_FORBIDDEN)
    if request.user.used_invite_code:
        return Response(data={'error': 'شما قبلاً از کد دعوت استفاده کرده‌اید.'}, status=status.HTTP_403_FORBIDDEN)
    else:
        try:
            inviter = User.objects.get(invite_id=invite_id)
        except Exception as e:
            return Response(data={'error': e}, status=status.HTTP_400_BAD_REQUEST)
        inviter.invitations_count = inviter.invitations_count + 1
        inviter.save()
        if inviter.invitations_count % int(config.DISCOUNT_INVITE_TRESHOLD) == 0:
            coupon = DiscountCoupon(title='تخفیف دعوت کاربر {}'.format(inviter.username),
                                    ref_num=str(hex(int((uuid.uuid4()).time_low))[2:]), single_user=True,
                                    percent=config.DISCOUNT_INVITE_PERCENT) # max_discount_amount, min_invoice_amount, expiration_date
            coupon.save()
            result = send_ultrafast_sms(mobile_num=inviter.mobile, template_id=2179, DiscountCode=coupon.ref_num,
                                        InvitationTreshold=config.DISCOUNT_INVITE_TRESHOLD,
                                        Percent=config.DISCOUNT_INVITE_PERCENT)
        request.user.used_invite_code = True
        request.user.save()
        return Response(data={'message': 'success'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def rate_order_view(request):
    if 'HTTP_X_REAL_IP' in request.META:
        ip = request.META['HTTP_X_REAL_IP']
    else:
        ip = request.META['REMOTE_ADDR']
    score = int(request.POST.get('score'))
    user = request.user or None
    try:
        content_type = ContentType.objects.get(app_label='service_delivery', model=request.POST.get('service_model'))
        service_object = content_type.get_object_for_this_type(pk=int(request.POST.get('order_id')))
    except Exception as e:
        return Response(data={'error': e}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # TODO order should be payed (status:done) for personnel to be rated
        existing_rating = UserRating.objects.for_instance_by_user(service_object, user)

        if existing_rating:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'شما قبلاً به این سفارش امتیاز داده‌اید'})
        else:
            rating = Rating.objects.rate(service_object, score, user=user, ip=ip)
            rating.save()
            personnel_new_rating = ((service_object.personnel.ratings_count * service_object.personnel.ratings) + score) / \
                                   (service_object.personnel.ratings_count + 1)
            service_object.personnel.ratings_count += 1
            service_object.personnel.ratings = personnel_new_rating
            service_object.personnel.save()
            service_object.status = 3
            service_object.save()
            return Response(data={'message': 'امتیاز با موفقیت ثبت شد.'}, status=status.HTTP_201_CREATED)
    except ValidationError as err:
        return Response(data={'error': err.message}, status=status.HTTP_400_BAD_REQUEST)


# header = {'X-CSRFToken':'2tSw9MRnKlwfIY2aMzdaBbZPgXcqLI2JH9hhz4QjLEXbpiqrLLlY34BivPS1WXKW'}
# cookie = {'csrftoken': '2tSw9MRnKlwfIY2aMzdaBbZPgXcqLI2JH9hhz4QjLEXbpiqrLLlY34BivPS1WXKW', 'sessionid':'pjyeinks9doeiex21h6w4sq8wpvahlcc'}
# r = requests.post('http://localhost:8000/rate-personnel/', data={'service_model':'electricity', 'order_id':6, 'score':3}, cookies=cookie, headers=header)

# TODO Handle errors


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def order_invoice_view(request):
    """
    create invoice for an order

    :request.data {content_type, object_id }
                    optional: discount (discount code), description
    :return: invoice_id, invoice_ref_num
    """
    try:
        # TODO get object. call calculate_price method.
        request.data['content_type'] = ContentType.objects.get(app_label='service_delivery',
                                                               model=request.data['content_type'])
        service_details = ServiceDetail.objects.get(content_type=request.data['content_type'])
        if 'discount' in request.data:
            request.data['discount'] = DiscountCoupon.objects.get(ref_num=request.data['discount'])
            # TODO cache active discounts and query in them
    except Exception as e:
        return Response(data={'error': e}, status=status.HTTP_400_BAD_REQUEST)
    discount_message = ''
    if request.data['discount']:
        # TODO if price > discount.min_invoice_amount and discount.is_active ...
        if request.data['discount'].service and request.data['discount'].service != service_details:
            discount_message = 'این تخفیف برای این نوع خدمت نیست'
        if datetime.now() > request.data['discount'].expiration_date:
            discount_message = 'این کوپن منقضی شده است'
        coupon_used = UsedDiscounts.objects.filter(client=request.user, discount_coupon=request.data['discount'])
        if coupon_used:
            discount_message = 'شما قبلاً از این کوپن استفاده کرده‌اید'
        if discount_message:
            request.data['discount'].amount = request.data['discount'].percent = 0
        if 'amount' in request.data['discount']:
            request.data['amount'] = service_details.price - request.data['discount'].amount
            if request.data['discount'].amount != 0:
                discount_message = 'شما {} تومان تخفیف دریافت کردید'.format(request.data['discount'].amount)
                UsedDiscounts.objects.create(client=request.user, discount_coupon=request.data['discount'])
                if request.data['discount'].single_user:
                    request.data['discount'].is_active = False
                    request.data['discount'].save()
        elif 'percent' in request.data['discount']:
            discount_amount = service_details.price * (request.data['discount'].percent / 100)
            if discount_amount > request.data['discount'].max_discount_amount:
                discount_amount = request.data['discount'].max_discount_amount
            if request.data['discount'].percent != 0:
                discount_message = 'شما {} تومان تخفیف دریافت کردید'.format(discount_amount)
                UsedDiscounts.objects.create(client=request.user, discount_coupon=request.data['discount'])
                if request.data['discount'].single_user:
                    request.data['discount'].is_active = False
                    request.data['discount'].save()
            request.data['amount'] = service_details.price - discount_amount
    else:
        request.data['amount'] = service_details.price

    invoice = Invoice.objects.create(**request.data)
    # generate_ref_num(request, invoice)
    response_data = {'invoice_id': invoice.id, 'ref_num': invoice.ref_num, 'amount': invoice.amount}
    if discount_message:
        response_data['discount_message'] = discount_message
    return Response(data={'invoice_id': invoice.id, 'ref_num': invoice.ref_num}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def invoice_payment_view(request):
    """
    create payment object from invoice and execute transaction
    :request {invoice (invoice pk), method (1: USSD, 2: Card, 3: Cash)}
    :return:
    """
    try:
        request.data['invoice'] = Invoice.objects.get(pk=request.data['invoice'])
    except Exception as e:
        return Response(data={'error': e}, status=status.HTTP_400_BAD_REQUEST)
    request.data['amount'] = request.data['invoice'].amount
    payment = PaymentTransaction.objects.create(**request.data)
    # generate_ref_num(request, payment)
    if request.data['method'] == 1:
        # USSD payment
        payment.status = 2  # being payed
        # perform payment
        # if payment successful:
        #   payment.status = 3
        #   update payment_code and ref_num
        #   .save()
        #   return success
        # else:
        #   payment.status = 1
        #   return error
        pass
    elif request.data['method'] == 2:
        # Card payment
        payment.status = 2  # being payed
        # perform payment
        # if payment successful:
        #   payment.status = 3
        #   update payment_code and ref_num
        #   .save()
        #   return success
        # else:
        # payment.status = 1
        # return error
        pass
    elif request.data['method'] == 3:
        # Cash
        request.data['invoice'].content_object.status = 3
        request.data['invoice'].content_object.save()
    return Response(data={'invoice_id': payment.id, 'ref_num': payment.ref_num}, status=status.HTTP_201_CREATED)


def send_job_requests(request):
    rule = re.compile(r'^09\d{9,11}$')
    name = request.POST.get('name')
    cell_num = request.POST.get('cell_num')
    form_type = request.POST.get('form_type')
    if name == '' or not rule.search(cell_num):
        return HttpResponse(status=403)
    skill = request.POST.get('skill')
    description = 'No description given'
    if request.POST.get('description'):
        description = request.POST.get('description')

    sg = sendgrid.SendGridAPIClient(apikey=config.SENDGRID_API_KEY)
    from_email = Email("karbama@karbamabnd.com")
    to_email = Email("info@karbamabnd.com")
    if skill:
        subject = '{}: {} - {} - {}'.format(form_type, skill, name, cell_num)
    else:
        subject = '{}: {} - {}'.format(form_type, name, cell_num)
    content = Content("text/plain", description)
    sent_mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=sent_mail.get())
    return HttpResponse(status=200)


def refresh_sms_token_view(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    next_url = request.GET['next']
    try:
        eager = refresh_sms_token.apply()
    except Exception as e:
        return HttpResponse(status=500)

    return redirect('Http://karbamabnd.com/admin' + next_url)


def send_app_download_link(request):
    rule = re.compile(r'^09\d{9,11}$')
    cell_num = request.POST.get('cell_num')
    if not rule.search(cell_num):
        return HttpResponse(status=403)
    try:
        saved_user = LinkRequestedNumbers.objects.get(mobile=cell_num)
    except LinkRequestedNumbers.DoesNotExist:
        saved_user = None
    if not saved_user:
        new_number = LinkRequestedNumbers.objects.create(mobile=cell_num)
        new_number.save()
    link = config.APP_DOWNLOAD_LINK
    result = send_ultrafast_sms(mobile_num=cell_num, template_id=2318, Link=link)
    if result:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def send_fast_sms(request):
    rule = re.compile(r'^09\d{9,11}$')
    if not rule.search(request.data['mobile_num']):
        return Response(data={'error': 'cell number invalid'}, status=status.HTTP_403_FORBIDDEN)
    result = send_ultrafast_sms(**request.data)
    if result:
        return Response(data={'error': 'sms was sent successfully'}, status=status.HTTP_200_OK)
    else:
        return Response(data={'error': 'server was unable to sens sms'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceDetailPagination(LimitOffsetPagination):
    default_limit = 15


class ServiceDetailView(generics.ListAPIView):
    queryset = ServiceDetail.objects.all()
    serializer_class = ServiceDetailSerializer
    pagination_class = ServiceDetailPagination

    def get_queryset(self):
        queryset = ServiceDetail.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active, city=self.request.query_params.get('city'))
        return queryset


class PaymentView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = Invoice

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     object_id = serializer.data['pk']
    #     electricity_ctype = ContentType.objects.get(model='Electricity')
    #     ref_num = str(electricity_ctype.id) + '-' + jdatetime.datetime.now().strftime("%Y%m%d%H%M%S")
    #     Order.objects.create(client=self.request.user, ref_num=ref_num, content_type=electricity_ctype,
    #                          object_id=object_id)
    #
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        # make sure to catch 404's below
        obj = queryset.get(pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)
        return obj


class ACViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AC.objects.all().order_by('-created')
    serializer_class = ACCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ACListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ACListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = ACDetailSerializer(instance)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        items = None
        if 'items' in request.data:
            items = request.data.pop('items')
        serializer = ACCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'ac')
        obj.client = request.user
        obj.save()
        if items:
            for item in items:
                ACItem.objects.create(ac_obj=obj, **item)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            # self.perform_destroy(instance)
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class AnnouncementViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Announcement.objects.all().order_by('-created')
    serializer_class = AnnouncementListSerializer
    filter_fields = ('is_active', 'is_ad')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AnnouncementDetailSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = AnnouncementDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)


class DryCleaningViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = DryCleaning.objects.all().order_by('-created')
    serializer_class = DryCleaningCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DryCleaningListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DryCleaningListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = DryCleaningDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + DryCleaning.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                if serializer.data['is_express']:
                    ios_data += 'تحوبل اکسپرس: ' + str(serializer.data['is_express']) + "\n"
                if serializer.data['delivery_time']:
                    ios_data += 'زمان تحویل: ' + str(serializer.data['delivery_time']) + "\n"
                if serializer.data['clothes']:
                    ios_data += 'البسه: ' + str(serializer.data['clothes']) + "\n"
                if serializer.data['blanket']:
                    ios_data += 'پتو: ' + str(serializer.data['blanket']) + "\n"
                if serializer.data['curtain']:
                    ios_data += 'پرده: ' + str(serializer.data['curtain']) + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = DryCleaningCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        test = obj.client
        # generate_ref_num(self.request, obj, 'drycleaning')
        obj.client = request.user
        obj.save()
        test = obj.client
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class CarpetCleaningViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CarpetCleaning.objects.all().order_by('-created')
    serializer_class = CarpetCleaningCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CarpetCleaningListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CarpetCleaningListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = CarpetCleaningDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + CarpetCleaning.STATUS_CHOICES[serializer.data['status'] - 1][1] + "\n"
                if serializer.data['wash']:
                    ios_data += 'شستشو: ' + str(serializer.data['wash']) + "\n"
                if serializer.data['stain']:
                    ios_data += 'لکه‌گیری: ' + str(serializer.data['stain']) + "\n"
                if serializer.data['patch']:
                    ios_data += 'رفوگری: ' + str(serializer.data['patch']) + "\n"
                if serializer.data['items']:
                    ios_data += 'موارد: '
                    for item in serializer.data['items']:
                        ios_data += '{ '
                        ios_data += 'نوع:' + CarpetCleaningItem.CARPET_CLEANING_TYPE_CHOICES[item['type'] - 1][1] + "\n"
                        ios_data += 'اندازه:' + CarpetCleaningItem.SIZE_CHOICES[item['size'] - 1][1] + "\n"
                        ios_data += 'نوع فرش:' + CarpetCleaningItem.CARPET_TYPE_CHOICES[item['carpet_type'] - 1][1] + "\n"
                        ios_data += '}, '
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        items = None
        if 'items' in request.data:
            items = request.data.pop('items')
        serializer = CarpetCleaningCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'carpetcleaning')
        obj.client = request.user
        obj.save()
        if items:
            for item in items:
                CarpetCleaningItem.objects.create(carpet_cleaning_obj=obj, **item)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class MedicalViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Medical.objects.all().order_by('-created')
    serializer_class = MedicalCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MedicalListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MedicalListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = MedicalDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + Medical.STATUS_CHOICES[serializer.data['status'] - 1][1] + "\n"
                if serializer.data['medic_gender']:
                    ios_data += 'جنسیت پزشک: ' + Medical.GENDER_CHOICES[serializer.data['medic_gender'] - 1][1] \
                                + "\n"
                if serializer.data['num_sessions']:
                    ios_data += 'تعداد جلسات: ' + str(serializer.data['num_sessions']) + "\n"
                if serializer.data['sessions']:
                    ios_data += 'جلسات: '
                    for item in serializer.data['sessions']:
                        ios_data += '{زمان: ' + str(item['date']) + '}' + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        items = None
        if 'items' in request.data:
            items = request.data.pop('items')
        serializer = MedicalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'medical')
        obj.client = request.user
        obj.save()
        if items:
            for item in items:
                MedicalSession.objects.create(medical_obj=obj, **item)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class HomeApplianceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = HomeAppliance.objects.all().order_by('-created')
    serializer_class = HomeApplianceCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HomeApplianceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HomeApplianceListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = HomeApplianceDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + HomeAppliance.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                if serializer.data['service_type']:
                    ios_data += 'نوع سرویس: ' + HomeAppliance.SERVICE_TYPE_CHOICES[serializer.data['service_type']-1][1] \
                                + "\n"
                if serializer.data['brand']:
                    ios_data += 'برند: ' + HomeAppliance.BRANDS_CHOICES[serializer.data['brand']-1][1] \
                                + "\n"
                if serializer.data['home_appliance_type']:
                    ios_data += 'نوع لوازم خانگی: ' + HomeAppliance.HOME_APPLIANCE_TYPE_CHOICES[serializer.data['home_appliance_type']-1][1] \
                                + "\n"
                if serializer.data['problem']:
                    ios_data += 'علائم خرابی: ' + HomeAppliance.PROBLEM_CHOICES[serializer.data['problem']-1][1] \
                                + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = HomeApplianceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'homeappliance')
        obj.client = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class PlumbingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Plumbing.objects.all().order_by('-created')
    serializer_class = PlumbingCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlumbingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PlumbingListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = PlumbingDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + Plumbing.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                if serializer.data['water_and_sewage']:
                    ios_data += 'آب و فاضلاب: ' + Plumbing.WATER_AND_SEWAGE_CHOICES[serializer.data['water_and_sewage']-1][1] \
                                + "\n"
                if serializer.data['water_heater']:
                    ios_data += 'آبگرمکن: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['water_heater']-1][1] \
                                + "\n"
                if serializer.data['squat_toilet']:
                    ios_data += 'توالت ایرانی: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['squat_toilet']-1][1] \
                                + "\n"
                if serializer.data['flush_toilet']:
                    ios_data += 'توالت فرنگی: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['flush_toilet']-1][1] \
                                + "\n"
                if serializer.data['flushing_system']:
                    ios_data += 'فلاش تانک: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['flushing_system']-1][1] \
                                + "\n"
                if serializer.data['faucets']:
                    ios_data += 'شیر‌آلات: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['faucets']-1][1] \
                                + "\n"
                if serializer.data['bathroom_sink']:
                    ios_data += 'روشویی: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['bathroom_sink']-1][1] \
                                + "\n"
                if serializer.data['kitchen_sink']:
                    ios_data += 'سینک ظرقشویی: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['kitchen_sink']-1][1] \
                                + "\n"
                if serializer.data['bath_tub']:
                    ios_data += 'وان حمام: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['bath_tub']-1][1] \
                                + "\n"
                if serializer.data['water_pump']:
                    ios_data += 'پمپ آب: ' + Plumbing.SERVICE_TYPE_CHOICES[serializer.data['water_pump']-1][1] \
                                + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = PlumbingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'plumbing')
        obj.client = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ElectricityViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Electricity.objects.all().order_by('-created')
    serializer_class = ElectricityCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ElectricityListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ElectricityListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = ElectricityDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + Electricity.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                if serializer.data['wiring']:
                    ios_data += 'سیم‌کشی: ' + Electricity.WIRING_CHOICES[serializer.data['wiring']-1][1] \
                                + "\n"
                if serializer.data['switch_and_socket']:
                    ios_data += 'کلید و پریز: ' + Electricity.WIRING_CHOICES[serializer.data['switch_and_socket']-1][1] \
                                + "\n"
                if serializer.data['lighting']:
                    ios_data += 'روشنایی: ' + Electricity.LIGHTING_CHOICES[serializer.data['lighting']-1][1] \
                                + "\n"
                if serializer.data['fuse_box']:
                    ios_data += 'جعبه فیوز: ' + Electricity.SERVICE_TYPE_CHOICES_1[serializer.data['fuse_box']-1][1] \
                                + "\n"
                if serializer.data['earth_wiring']:
                    ios_data += 'سیم‌کشی ارث: ' + Electricity.SERVICE_TYPE_CHOICES_1[serializer.data['earth_wiring']-1][1] \
                                + "\n"
                if serializer.data['phone_and_central_wiring']:
                    ios_data += 'سیم‌کشی تلفن و سانترال: ' + Electricity.PHONE_AND_CENTRAL_CHOICES[serializer.data['phone_and_central_wiring']-1][1] \
                                + "\n"
                if serializer.data['ventilation']:
                    ios_data += 'هواکش: ' + Electricity.SERVICE_TYPE_CHOICES_1[serializer.data['ventilation']-1][1] \
                                + "\n"
                if serializer.data['ventilation_and_common_spaces']:
                    ios_data += 'هواکش و مشاعات: ' + Electricity.SERVICE_TYPE_CHOICES_2[serializer.data['ventilation_and_common_spaces']-1][1] \
                                + "\n"
                if serializer.data['central_antenna']:
                    ios_data += 'آنتن مرکزی: ' + Electricity.SERVICE_TYPE_CHOICES_1[serializer.data['central_antenna']-1][1] \
                                + "\n"
                if serializer.data['video_intercom']:
                    ios_data += 'آیفون تصویری: ' + Electricity.SERVICE_TYPE_CHOICES_1[serializer.data['video_intercom']-1][1] \
                                + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = ElectricityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'electricity')
        obj.client = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class TuitionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Tuition.objects.all().order_by('-created')
    serializer_class = TuitionCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TuitionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TuitionListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = TuitionDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + Truck.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                if serializer.data['level']:
                    ios_data += 'مقطع تحصیلی: ' + Tuition.LEVEL_CHOICES[serializer.data['level']-1][1] \
                                + "\n"
                if serializer.data['grade']:
                    ios_data += 'پایه تحصیلی: ' + Tuition.GRADE_CHOICES[serializer.data['grade']-1][1] \
                                + "\n"
                if serializer.data['lesson_name']:
                    ios_data += 'اسم درس: ' + Tuition.LESSON_NAME_CHOICES[serializer.data['lesson_name']-1][1] \
                                + "\n"
                if serializer.data['tutor_gender']:
                    ios_data += 'جنسیت استاد: ' + Tuition.TUTOR_GENDER_CHOICES[serializer.data['tutor_gender']-1][1] \
                                + "\n"
                if serializer.data['student_gender']:
                    ios_data += 'جنسیت دانش‌آموز: ' + Tuition.TUTOR_GENDER_CHOICES[serializer.data['student_gender']-1][1] \
                                + "\n"
                if serializer.data['num_sessions']:
                    ios_data += 'تعداد جلسات: ' + str(serializer.data['num_sessions']) + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = TuitionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'tuition')
        obj.client = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class TruckViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Truck.objects.all().order_by('-created')
    serializer_class = TruckCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TruckListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TruckListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = TruckDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + Truck.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                if serializer.data['truck_type']:
                    ios_data += 'نوع اتوبار: ' + Truck.TRUCK_TYPE_CHOICES[serializer.data['truck_type']-1][1] \
                                + "\n"
                if serializer.data['num_worker']:
                    ios_data += 'تعداد کارگران: ' + str(serializer.data['num_worker']) + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = TruckCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'truck')
        obj.client = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class CleaningViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Cleaning.objects.all().order_by('-created')
    serializer_class = CleaningCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(client=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CleaningListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CleaningListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            serializer = CleaningDetailSerializer(instance)
            if request.query_params.get('ios') == 'true':
                ios_data = ''
                if serializer.data['schedule_time']:
                    ios_data += 'زمان ارائه خدمت: ' + serializer.data['schedule_time'] + "\n"
                if serializer.data['personnel']:
                    ios_data += 'اسم پرسنل: ' + serializer.data['personnel']['first_name'] + ' ' + \
                                serializer.data['personnel']['last_name'] + "\n"
                    ios_data += 'موبایل پرسنل: ' + serializer.data['personnel']['mobile'] + "\n"
                if serializer.data['address']:
                    ios_data += 'آدرس: ' + serializer.data['address'] + "\n"
                if serializer.data['description']:
                    ios_data += 'توضیحات: ' + serializer.data['description'] + "\n"
                if serializer.data['building_type']:
                    ios_data += 'نوع مکان: ' + Cleaning.BUILDING_TYPE_CHOICES[serializer.data['building_type']-1][1] \
                                + "\n"
                if serializer.data['hour']:
                    ios_data += 'مقدار ساعت: ' + str(serializer.data['hour']) + "\n"
                if serializer.data['male_worker_num']:
                    ios_data += 'تعداد نیروی مرد: ' + str(serializer.data['male_worker_num']) + "\n"
                if serializer.data['female_worker_num']:
                    ios_data += 'تعداد نیروی زن: ' + str(serializer.data['female_worker_num']) + "\n"
                if serializer.data['status']:
                    ios_data += 'وضعیت: ' + Cleaning.STATUS_CHOICES[serializer.data['status']-1][1] + "\n"
                return Response(ios_data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = CleaningCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # generate_ref_num(self.request, obj, 'cleaning')
        obj.client = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.client == self.request.user:
            instance.status = 4
            instance.is_active = False
            instance.save()
            return Response(data={'message': 'سفارش با موفقیت لفو شد.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

# header = {'Authorization': 'Token 06faeece554f8a91cd3d1f7cab0d7dccb557246a'}
# r = requests.get('http://localhost:8000/electricities', headers=header)
# TODO debug method not allowed 405
# TODO payment done/cancelled -> change is_active to false
# TODO override get_serializer_class for different serializer (generics.py) "read the comments"
# TODO CHANGED!

#
# import logging
# log = logging.getLogger('gunicorn.access')
# log.info('hiiii')