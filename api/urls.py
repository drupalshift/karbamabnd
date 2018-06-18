from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
from rest_framework import routers


router = routers.SimpleRouter()
# router.register(r'orders', OrderViewSet)
router.register(r'acs', ACViewSet)
router.register(r'drycleanings', DryCleaningViewSet)
router.register(r'carpetcleanings', CarpetCleaningViewSet)
router.register(r'medicals', MedicalViewSet)
router.register(r'homeappliances', HomeApplianceViewSet)
router.register(r'plumbings', PlumbingViewSet)
router.register(r'electricities', ElectricityViewSet)
router.register(r'tuitions', TuitionViewSet)
router.register(r'trucks', TruckViewSet)
router.register(r'cleanings', CleaningViewSet)
router.register(r'announcements', AnnouncementViewSet)


urlpatterns = router.urls

urlpatterns = format_suffix_patterns(urlpatterns)


