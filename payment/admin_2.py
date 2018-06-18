from django.contrib import admin
from .models import *


@admin.register(DiscountCoupon)
class DiscountCouponAdmin(admin.ModelAdmin):
    list_display = ('ref_num', 'service', 'amount', 'percent', 'expiration_date')
    search_fields = ['ref_num']
    list_filter = ('amount', 'percent', 'created', 'expiration_date')


class OrderItemsInLine(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # fields = ('name', 'title')
    # exclude = ('birth_date',)
    # fieldsets = (
    #     (None, {
    #         'fields': (('url', 'title'), 'content', 'sites')
    #     }),
    #     ('Advanced options', {
    #         'classes': ('collapse',),
    #         'fields': ('registration_required', 'template_name'),
    #     }),
    # )
    readonly_fields = ('client',)
    list_display = ('ref_num', 'client', '_orderitems')
    search_fields = ['ref_num']
    list_filter = ('created', 'client')
    date_hierarchy = 'created'
    empty_value_display = '-empty-'

    inlines = [
        OrderItemsInLine
    ]

    def _orderitems(self, obj):
        return obj.orderitem_set.all().count()


class InvoiceItemsInLine(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('order',)
    list_display = ('ref_num', 'order', '_invoiceitems')
    search_fields = ['ref_num']
    list_filter = ('created',)

    inlines = [
        InvoiceItemsInLine
    ]

    def _invoiceitems(self, obj):
        return obj.invoiceitem_set.all().count()


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('Invoice',)
    list_display = ('Invoice', 'amount', 'status', 'method', 'card_number', 'payment_code')
    search_fields = ['payment_code']
    list_filter = ('amount', 'status', 'method', 'created')

