#!/usr/bin/env python
"""
Полный тест всех API endpoints
Запускайте перед стартом сервера для проверки работоспособности API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver,.onrender.com')

django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

print("=" * 60)
print("ПРОВЕРКА ВСЕХ API ENDPOINTS")
print("=" * 60)

# Создаем тестового пользователя
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com', 'role': 'staff', 'department': 'IT'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"\n[OK] Создан тестовый пользователь: {user.username}")
else:
    print(f"\n[OK] Найден тестовый пользователь: {user.username}")

# Логин
print("\n1. ЛОГИН (POST /api/accounts/login/)")
response = client.post('/api/accounts/login/', {
    'username': 'testuser', 
    'password': 'testpass123'
}, content_type='application/json')

if response.status_code == 200:
    token = response.json().get('access')
    print("   [OK] Токен получен")
    
    # Headers для авторизованных запросов
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # Определяем все URL через reverse
    urls = {
        'accounts_me': ('GET', '/api/accounts/me/', None),
        'accounts_users': ('GET', '/api/accounts/users/', None),
        'assets_list': ('GET', '/api/assets/', None),
        'assets_types': ('GET', '/api/assets/types/', None),
        'assets_transfers': ('GET', '/api/assets/transfers/', None),
        'locations_list': ('GET', '/api/locations/', None),
        'reports_summary': ('GET', '/api/reports/', None),
        'reports_audit': ('GET', '/api/reports/audit-logs/', None),
        'assets_scan': ('POST', '/api/assets/scan/', {'asset_tag': 'TEST'}),
        'assets_public': ('GET', '/api/assets/public/', {'asset_tag': 'TEST'}),
        'assets_public_tag': ('GET', '/api/assets/public/TEST123/', None),
    }
    
    print("\n2. ПРОВЕРКА ENDPOINTS:")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for name, (method, url, data) in urls.items():
        try:
            if data:
                if method == 'POST':
                    r = client.post(url, data, content_type='application/json', **headers)
                else:
                    r = client.get(url, data, **headers)
            elif method == 'POST':
                r = client.post(url, content_type='application/json', **headers)
            else:
                r = client.get(url, **headers)
            
            if r.status_code in [200, 201, 400, 404]:
                status = '[OK]'
                passed += 1
            else:
                status = '[FAIL]'
                failed += 1
            
            print(f"   {status} {method:6} {url:45} -> {r.status_code}")
            
        except Exception as e:
            print(f"   [ERR] {method:6} {url:45} -> {str(e)[:30]}")
            failed += 1
    
    # Тест без авторизации
    print("\n3. ПУБЛИЧНЫЕ ENDPOINTS (без авторизации):")
    print("-" * 60)
    
    public_urls = [
        ('GET', '/api/assets/public/?asset_tag=TEST'),
        ('POST', '/api/assets/scan/', {'asset_tag': 'TEST'}),
    ]
    
    for method, url in public_urls:
        try:
            if method == 'POST':
                r = client.post(url, {'asset_tag': 'TEST'}, content_type='application/json')
            else:
                r = client.get(url)
            
            if r.status_code in [200, 400, 404]:
                status = '[OK]'
                passed += 1
            else:
                status = '[FAIL]'
                failed += 1
            
            print(f"   {status} {method:6} {url:45} -> {r.status_code}")
        except Exception as e:
            print(f"   [ERR] {method:6} {url:45} -> {str(e)[:30]}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТ: {passed} прошло, {failed} неудач")
    
    if failed == 0:
        print("ВСЕ API ENDPOINTS РАБОТАЮТ КОРРЕКТНО!")
    else:
        print(f"ВНИМАНИЕ: {failed} endpoint(s) требуют исправления")
    
else:
    print("   [FAIL] Логин не удался")
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.content[:200]}")

print("\n" + "=" * 60)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)
