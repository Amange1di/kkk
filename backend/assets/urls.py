from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, TransferHistoryViewSet, AssetTypeViewSet

router = DefaultRouter()
router.register(r'', AssetViewSet)
router.register(r'transfers', TransferHistoryViewSet)
router.register(r'types', AssetTypeViewSet, basename='assettype')

urlpatterns = [
    path('', include(router.urls)),
]
