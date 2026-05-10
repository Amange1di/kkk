from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, TransferHistoryViewSet, AssetTypeViewSet, public_asset_scan

# Создаём роутер для основных endpoints
router = DefaultRouter()
router.register(r'', AssetViewSet, basename='asset')
router.register(r'transfers', TransferHistoryViewSet, basename='transfer')
router.register(r'types', AssetTypeViewSet, basename='assettype')

# URL конфигурация - публичные пути ДО router.urls
urlpatterns = [
    # Публичные endpoints без авторизации (первыми!)
    path('public/', public_asset_scan, name='public-asset-scan'),
    path('public/<str:asset_tag>/', public_asset_scan, name='public-asset-scan-by-tag'),
    path('scan/', public_asset_scan, name='asset-scan'),
]

# Добавляем все пути из роутера (types, transfers, assets)
urlpatterns.extend(router.urls)