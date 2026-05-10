#!/usr/bin/env python
"""
Полный тест всех API endpoints через прямой запрос к Django URL resolver
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver,.onrender.com')

django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from assets.views import public_asset_scan, AssetViewSet, AssetTypeViewSet, TransferHistoryViewSet

User = get_user_model()

print("=" * 60)
print("ПРОВЕРКА API VIEWS (прямой вызов)")
print("=" * 60)

# Создаем тестового пользователя
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com', 'role': 'staff', 'department': 'IT', 'is_active': True}
)
if created:
    user.set_password('testpass123')
    user.save()

print(f"[OK] Пользователь: {user.username}")

# Создаем тестовый актив
from assets.models import Asset, AssetType

asset_type, _ = AssetType.objects.get_or_create(name='Тестовый тип', code='TEST', defaults={'is_active': True})

asset, created = Asset.objects.get_or_create(
    asset_tag='TEST123',
    defaults={
        'name': 'Тестовый актив',
        'asset_type': asset_type,
        'status': 'available',
        'manufacturer': 'Test',
        'model': 'TestModel'
    }
)
print(f"[OK] Актив: {asset.asset_tag}")

# Прямой тест public_asset_scan
factory = RequestFactory()

print("\n1. ПРОВЕРКА public_asset_scan (GET с query params):")
request = factory.get('/api/assets/public/', {'asset_tag': 'TEST123'})
request.user = user
response = public_asset_scan(request)
print(f"   Статус: {response.status_code}")
if response.status_code == 200:
    print(f"   [OK] Актив найден: {response.data.get('asset', {}).get('asset_tag')}")
else:
    print(f"   [FAIL] {response.data}")

print("\n2. ПРОВЕРКА public_asset_scan (POST с body):")
request = factory.post('/api/assets/scan/', {'asset_tag': 'TEST123'}, content_type='application/json')
request.user = user
response = public_asset_scan(request)
print(f"   Статус: {response.status_code}")
if response.status_code == 200:
    print(f"   [OK] Актив найден: {response.data.get('asset', {}).get('asset_tag')}")
else:
    print(f"   [FAIL] {response.data}")

print("\n3. ПРОВЕРКА public_asset_scan (несуществующий актив):")
request = factory.get('/api/assets/public/', {'asset_tag': 'NOTEXIST'})
request.user = user
response = public_asset_scan(request)
print(f"   Статус: {response.status_code}")
if response.status_code == 404:
    print(f"   [OK] Возвращен 404 как и ожидалось")
else:
    print(f"   [FAIL] Ожидался 404, получен {response.status_code}")

# Тест AssetTypeViewSet
print("\n4. ПРОВЕРКА AssetTypeViewSet:")
from rest_framework.test import APIRequestFactory
factory = APIRequestFactory()

request = factory.get('/api/assets/types/')
request.user = user

view = AssetTypeViewSet.as_view({'get': 'list'})
response = view(request)
print(f"   Статус: {response.status_code}")
if response.status_code == 200:
    print(f"   [OK] Типы активов: {len(response.data)} шт.")
else:
    print(f"   [FAIL] {response.data}")

# Тест TransferHistoryViewSet
print("\n5. ПРОВЕРКА TransferHistoryViewSet:")
request = factory.get('/api/assets/transfers/')
request.user = user

view = TransferHistoryViewSet.as_view({'get': 'list'})
response = view(request)
print(f"   Статус: {response.status_code}")
if response.status_code == 200:
    print(f"   [OK] История перемещений: {len(response.data)} шт.")
else:
    print(f"   [FAIL] {response.data}")

print("\n" + "=" * 60)
print("ПРОВЕРКА VIEWS ЗАВЕРШЕНА")
print("=" * 60)
