"""karbama URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import *
from service_delivery.views import *
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    # path(r'report_builder/', include('report_builder.urls')),
    path(r'api/servicedetails/', ServiceDetailView.as_view()),
    path(r'api/towing/', TowingView.as_view()),
    path(r'api/rate-order/', rate_order_view),
    path(r'api/generate-invoice/', order_invoice_view),
    path(r'api/invoice-payment/', invoice_payment_view),
    path(r'api/user-orders/', UserOrderList.as_view()),
    path(r'api/user-orders-test/', BaseServiceView.as_view()),
    path(r'api/user-details/', UserDetailsView.as_view()),
    path(r'api/order-details/', order_details_view),
    path(r'api/latest-orders/', get_latest_orders_ajax),
    path(r'api/user-invite/', user_invite_view),
    path(r'api/use-discount/', use_discount_view),
    path(r'send-job-requests/', send_job_requests),
    path(r'send-app-download-link/', send_app_download_link),
    path(r'send-fast-sms/', send_fast_sms),
    path(r'refresh-sms-token/', refresh_sms_token_view),
    path(r'get-support-number/', get_support_number),
    path(r'get-app-version/', get_app_version),
    path(r'get-express-delivery-constant/', get_express_delivery_constant),
    path(r'', include('drfpasswordless.urls')),
    path('', HomePageView.as_view(), name='home'),
    path(r'about-us/', AboutUsView.as_view(), name='about-us'),
    path(r'terms-and-conditions/', TermsConditionsView.as_view(), name='terms-and-conditions'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('390083.txt', serve_enamad_confirmation, name='enamad-verification')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
