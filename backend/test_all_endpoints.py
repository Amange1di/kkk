#!/usr/bin/env python
"""
Тестирование всех endpoints бекенда: POST, PUT, PATCH, DELETE
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

# Add testserver to ALLOWED_HOSTS для тестов
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from assets.models import Asset, AssetType, TransferHistory
from locations.models import Location
from reports.models import AuditLog, ExportLog

UserModel = get_user_model()

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def create_test_data():
    """Создание тестовых данных"""
    print_section("Создание тестовых данных")
    
    # Создаём супер-админа
    admin, created = UserModel.objects.get_or_create(
        username='test_admin',
        defaults={
            'email': 'admin@test.com',
            'role': 'inventory_manager',
            'is_active': True
        }
    )
    if created:
        admin.set_password('testpass123')
        admin.save()
        print(f"✓ Создан admin: {admin.username}")
    else:
        # Обновляем роль если нужно
        if admin.role != 'inventory_manager':
            admin.role = 'inventory_manager'
            admin.save()
        print(f"✓ Admin существует: {admin.username}")
    
    # Создаём пользователя
    user, created = UserModel.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'user@test.com',
            'role': 'staff',
            'is_active': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Создан user: {user.username}")
    else:
        print(f"✓ User существует: {user.username}")
    
    # Создаём локацию
    location, created = Location.objects.get_or_create(
        name='Test Room',
        defaults={
            'location_type': 'room',
            'building': 'Main',
            'floor': '1',
            'is_active': True
        }
    )
    if created:
        print(f"✓ Создана локация: {location.name}")
    else:
        print(f"✓ Локация существует: {location.name}")
    
    # Создаём тип актива
    asset_type, created = AssetType.objects.get_or_create(
        code='laptop',
        defaults={
            'name': 'Laptop',
            'description': 'Test laptop type',
            'is_active': True
        }
    )
    if created:
        print(f"✓ Создан тип актива: {asset_type.name}")
    else:
        print(f"✓ Тип актива существует: {asset_type.name}")
    
    return admin, user, location, asset_type

def test_users(client, admin):
    """Тестирование endpoints пользователей"""
    print_section("TEST: Users Endpoints")
    
    # Login
    print("\n1. POST /api/accounts/login/")
    resp = client.post('/api/accounts/login/', {
        'username': 'test_admin',
        'password': 'testpass123'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    if resp.status_code == 200:
        data = resp.json()
        access_token = data.get('access')
        print(f"   Access token: {access_token[:20]}...")
    else:
        print(f"   Response: {resp.content.decode()}")
        return None
    
    # Set auth header
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    
    # Get current user
    print("\n2. GET /api/accounts/me/")
    resp = client.get('/api/accounts/me/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # List users
    print("\n3. GET /api/accounts/users/")
    resp = client.get('/api/accounts/users/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Create user
    print("\n4. POST /api/accounts/users/")
    resp = client.post('/api/accounts/users/', {
        'username': 'test_create_user',
        'email': 'create@test.com',
        'password': 'testpass123',
        'role': 'staff',
        'first_name': 'Test',
        'last_name': 'User'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    if resp.status_code in [200, 201]:
        created_user_id = resp.json().get('id')
        print(f"   Created user ID: {created_user_id}")
    else:
        print(f"   Response: {resp.content.decode()}")
        return None
    
    # Update user
    print("\n5. PUT /api/accounts/users/{id}/")
    if 'created_user_id' in dir():
        resp = client.put(f'/api/accounts/users/{created_user_id}/', {
            'username': 'test_create_user',
            'email': 'updated@test.com',
            'role': 'staff',
            'first_name': 'Updated',
            'last_name': 'Name',
            'password': 'testpass123'
        }, content_type='application/json')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # PATCH user
    print("\n6. PATCH /api/accounts/users/{id}/")
    if 'created_user_id' in dir():
        resp = client.patch(f'/api/accounts/users/{created_user_id}/', {
            'first_name': 'Patched'
        }, content_type='application/json')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Delete user
    print("\n7. DELETE /api/accounts/users/{id}/")
    if 'created_user_id' in dir():
        resp = client.delete(f'/api/accounts/users/{created_user_id}/')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 204 else '✗'}")
    
    # Logout
    print("\n8. POST /api/accounts/logout/")
    resp = client.post('/api/accounts/logout/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    return access_token

def test_locations(client, location):
    """Тестирование endpoints локаций"""
    print_section("TEST: Locations Endpoints")
    
    # List locations
    print("\n1. GET /api/locations/")
    resp = client.get('/api/locations/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Create location
    print("\n2. POST /api/locations/")
    resp = client.post('/api/locations/', {
        'name': 'Test Location Create',
        'location_type': 'room',
        'building': 'Test',
        'floor': '2',
        'is_active': True
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    if resp.status_code in [200, 201]:
        created_loc_id = resp.json().get('id')
        print(f"   Created location ID: {created_loc_id}")
    else:
        print(f"   Response: {resp.content.decode()}")
        return
    
    # Get location
    print("\n3. GET /api/locations/{id}/")
    if 'created_loc_id' in dir():
        resp = client.get(f'/api/locations/{created_loc_id}/')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Update location
    print("\n4. PUT /api/locations/{id}/")
    if 'created_loc_id' in dir():
        resp = client.put(f'/api/locations/{created_loc_id}/', {
            'name': 'Test Location Create Updated',
            'location_type': 'room',
            'building': 'Test',
            'floor': '2',
            'is_active': True
        }, content_type='application/json')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # PATCH location
    print("\n5. PATCH /api/locations/{id}/")
    if 'created_loc_id' in dir():
        resp = client.patch(f'/api/locations/{created_loc_id}/', {
            'floor': '3'
        }, content_type='application/json')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Delete location
    print("\n6. DELETE /api/locations/{id}/")
    if 'created_loc_id' in dir():
        resp = client.delete(f'/api/locations/{created_loc_id}/')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 204 else '✗'}")

def test_asset_types(client, asset_type):
    """Тестирование endpoints типов активов"""
    print_section("TEST: Asset Types Endpoints")
    
    # List asset types
    print("\n1. GET /api/assets/types/")
    resp = client.get('/api/assets/types/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Create asset type
    print("\n2. POST /api/assets/types/")
    resp = client.post('/api/assets/types/', {
        'name': 'Test Type Create',
        'code': 'test_type_create',
        'description': 'Test type description',
        'is_active': True
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    if resp.status_code in [200, 201]:
        created_type_id = resp.json().get('id')
        print(f"   Created type ID: {created_type_id}")
    else:
        print(f"   Response: {resp.content.decode()}")
        return
    
    # Get asset type
    print("\n3. GET /api/assets/types/{id}/")
    if 'created_type_id' in dir():
        resp = client.get(f'/api/assets/types/{created_type_id}/')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Update asset type
    print("\n4. PUT /api/assets/types/{id}/")
    if 'created_type_id' in dir():
        resp = client.put(f'/api/assets/types/{created_type_id}/', {
            'name': 'Test Type Create Updated',
            'code': 'test_type_create',
            'description': 'Updated description',
            'is_active': True
        }, content_type='application/json')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # PATCH asset type
    print("\n5. PATCH /api/assets/types/{id}/")
    if 'created_type_id' in dir():
        resp = client.patch(f'/api/assets/types/{created_type_id}/', {
            'is_active': False
        }, content_type='application/json')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Delete asset type
    print("\n6. DELETE /api/assets/types/{id}/")
    if 'created_type_id' in dir():
        resp = client.delete(f'/api/assets/types/{created_type_id}/')
        print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 204 else '✗'}")

def test_assets(client, location, asset_type, admin):
    """Тестирование endpoints активов"""
    print_section("TEST: Assets Endpoints")
    
    # Create asset first
    print("\n0. Creating test asset...")
    asset = Asset.objects.create(
        asset_tag='TEST001',
        name='Test Asset',
        description='Test asset for endpoint testing',
        asset_type=asset_type,
        current_location=location,
        status='available',
        manufacturer='Test',
        model='Model X',
        serial_number='SN123456',
        purchase_price=1000.00,
        currency='RUB',
        created_by=admin
    )
    print(f"   Created asset ID: {asset.id}, Tag: {asset.asset_tag}")
    
    # List assets
    print("\n1. GET /api/assets/")
    resp = client.get('/api/assets/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Get asset
    print("\n2. GET /api/assets/{id}/")
    resp = client.get(f'/api/assets/{asset.id}/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Update asset
    print("\n3. PUT /api/assets/{id}/")
    resp = client.put(f'/api/assets/{asset.id}/', {
        'asset_tag': 'TEST001',
        'name': 'Test Asset Updated',
        'description': 'Updated description',
        'asset_type': asset_type.id,
        'current_location': location.id,
        'status': 'available',
        'manufacturer': 'Test',
        'model': 'Model X',
        'serial_number': 'SN123456',
        'purchase_price': 1000.00,
        'currency': 'RUB'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # PATCH asset
    print("\n4. PATCH /api/assets/{id}/")
    resp = client.patch(f'/api/assets/{asset.id}/', {
        'name': 'Patched Asset'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Asset checkout
    print("\n5. POST /api/assets/{id}/checkout/")
    resp = client.post(f'/api/assets/{asset.id}/checkout/', {
        'assigned_to': admin.id,
        'reason': 'Test checkout'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Asset checkin
    print("\n6. POST /api/assets/{id}/checkin/")
    resp = client.post(f'/api/assets/{asset.id}/checkin/', {
        'reason': 'Test checkin'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Asset QR code
    print("\n7. GET /api/assets/{id}/qr_code/")
    resp = client.get(f'/api/assets/{asset.id}/qr_code/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Asset scan
    print("\n8. POST /api/assets/scan/")
    resp = client.post('/api/assets/scan/', {
        'asset_tag': 'TEST001'
    }, content_type='application/json')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code in [200, 201] else '✗'}")
    
    # Delete asset
    print("\n9. DELETE /api/assets/{id}/")
    resp = client.delete(f'/api/assets/{asset.id}/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 204 else '✗'}")

def test_reports(client):
    """Тестирование endpoints отчётов"""
    print_section("TEST: Reports Endpoints")
    
    # Reports summary
    print("\n1. GET /api/reports/")
    resp = client.get('/api/reports/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Reports assets summary (underscore in URL)
    print("\n2. GET /api/reports/assets_summary/")
    resp = client.get('/api/reports/assets_summary/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Reports export CSV
    print("\n3. GET /api/reports/export/?format=csv")
    resp = client.get('/api/reports/export/?format=csv')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")
    
    # Audit logs
    print("\n4. GET /api/reports/audit-logs/")
    resp = client.get('/api/reports/audit-logs/')
    print(f"   Status: {resp.status_code} {'✓' if resp.status_code == 200 else '✗'}")


def main():
    print("="*60)
    print("  TEST ALL BACKEND ENDPOINTS")
    print("="*60)
    
    # Create test data
    admin, user, location, asset_type = create_test_data()
    
    # Create client with auth
    client = Client()
    client.defaults['HTTP_AUTHORIZATION'] = ''
    
    # Get token
    resp = client.post('/api/accounts/login/', {
        'username': 'test_admin',
        'password': 'testpass123'
    }, content_type='application/json')
    if resp.status_code == 200:
        access_token = resp.json().get('access')
        client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        print(f"\n✓ Auth token obtained")
    else:
        print(f"\n✗ Failed to get auth token")
        return
    
    # Run all tests
    test_users(client, admin)
    test_locations(client, location)
    test_asset_types(client, asset_type)
    test_assets(client, location, asset_type, admin)
    test_reports(client)
    
    print_section("TEST SUMMARY")
    print("Все тесты завершены. Проверьте результаты выше.")
    print("="*60)

if __name__ == '__main__':
    main()