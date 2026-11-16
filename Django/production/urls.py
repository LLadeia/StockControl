from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductionLogViewSet,
    ProductRawMaterialViewSet,
    ProductViewSet,
    RawMaterialViewSet,
    get_user_info,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'raw-materials', RawMaterialViewSet)
router.register(r'product-raw-materials', ProductRawMaterialViewSet)
router.register(r'production-logs', ProductionLogViewSet, basename='production-log')

urlpatterns = [
    path('auth/user/', get_user_info, name='user-info'),
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
