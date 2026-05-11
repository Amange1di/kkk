from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, TransferHistoryViewSet, AssetTypeViewSet, public_asset_scan

# Создаём роутер для основных endpoints
router = DefaultRouter()
router.register(r'', AssetViewSet, basename='asset')
router.register(r'transfers', TransferHistoryViewSet, basename='transfer')
router.register(r'types', AssetTypeViewSet, basename='assettype')

# URL конфигурация - явно прописываем маршруты роутера
urlpatterns = [
    # Маршруты роутера (явно прописаны, чтобы не перехватывались public/<str:asset_tag>)
    path('types/', AssetTypeViewSet.as_view({'get': 'list', 'post': 'create'}), name='assettype-list-create'),
    path('types/<int:pk>/', AssetTypeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='assettype-detail'),
    path('transfers/', TransferHistoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='transfer-list-create'),
    path('transfers/<int:pk>/', TransferHistoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='transfer-detail'),
    path('', AssetViewSet.as_view({'get': 'list', 'post': 'create'}), name='asset-list-create'),
    path('<int:pk>/', AssetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='asset-detail'),
    # Custom actions для активов
    path('<int:pk>/checkout/', AssetViewSet.as_view({'post': 'checkout'}), name='asset-checkout'),
    path('<int:pk>/checkin/', AssetViewSet.as_view({'post': 'checkin'}), name='asset-checkin'),
    path('<int:pk>/transfer/', AssetViewSet.as_view({'post': 'transfer'}), name='asset-transfer'),
    path('<int:pk>/report_damage/', AssetViewSet.as_view({'post': 'report_damage'}), name='asset-report-damage'),
    path('<int:pk>/qr_code/', AssetViewSet.as_view({'get': 'qr_code'}), name='asset-qr-code'),
    path('scan/', public_asset_scan, name='asset-scan'),
    # Публичные endpoints без авторизации (в конце!)
    path('public/<str:asset_tag>/', public_asset_scan, name='public-asset-scan-by-tag'),
    path('public/', public_asset_scan, name='public-asset-scan'),
]