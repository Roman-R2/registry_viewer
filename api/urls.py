from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import LRPApiViewSet

app_name = 'api'

router = DefaultRouter()

# Эндпоинты статистики по бэкапам из лог-файлов TSM на серверах
router.register('lrp_registry', LRPApiViewSet, basename="lrp_registry")

urlpatterns = [
    path('v1/', include(router.urls)),
]
