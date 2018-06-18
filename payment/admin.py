from django.contrib import admin
from .models import *


@admin.register(DiscountCoupon)
class DiscountCouponAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)
    list_display = ('title', 'ref_num', 'service', 'amount', 'percent', 'single_user', 'expiration_date')
    fields = (('is_active', 'ref_num', 'title', 'single_user', 'service'),
              ('amount', 'percent', 'max_discount_amount', 'min_invoice_amount'),
              ('expiration_date',),
              ('description',))
    search_fields = ['ref_num']
    list_filter = ('single_user', 'amount', 'percent', 'created', 'expiration_date')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('ref_num', 'content_type', 'amount', 'created')
    fields = (('ref_num', 'content_type', 'object_id'),
              ('discount', 'amount'),
              ('description',))
    search_fields = ['ref_num']
    list_filter = ('created', 'content_type')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('invoice', 'amount')
    list_display = ('ref_num', 'invoice', 'amount', 'status', 'method', 'card_number',)
    fields = (('payment_code', 'ref_num', 'status'),
              ('invoice', 'amount'),
              ('method', 'card_number'),
              ('description',))
    search_fields = ['payment_code']
    list_filter = ('status', 'method', 'created')


@admin.register(UsedDiscounts)
class UsedDiscountAdmin(admin.ModelAdmin):
    list_display = ('client', 'discount_coupon')
    search_fields = ['client', 'discount_coupon']
