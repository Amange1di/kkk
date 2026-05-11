import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from rest_framework.test import APIClient
from accounts.models import CustomUser

client = APIClient()

# Get admin user and force authenticate
admin = CustomUser.objects.get(username='test_admin')
client.force_authenticate(user=admin)

# Test export
print('Testing /api/reports/export/?format=csv')
resp = client.get('/api/reports/export/?format=csv')
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    print('Content-Type:', resp.get('Content-Type', 'N/A'))
else:
    print('Response:', resp.content.decode()[:200])

# Test assets-summary
print('\nTesting /api/reports/assets-summary/')
resp = client.get('/api/reports/assets-summary/')
print(f'Status: {resp.status_code}')

