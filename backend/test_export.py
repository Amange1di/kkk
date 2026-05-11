import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from rest_framework.test import APIClient
from accounts.models import CustomUser
from assets.models import Asset, AssetType
from locations.models import Location

# Создаём тестовые данные для экспорта
admin = CustomUser.objects.get(username='test_admin')
location, _ = Location.objects.get_or_create(name='Export Test', defaults={'location_type': 'room', 'is_active': True})
asset_type, _ = AssetType.objects.get_or_create(code='export_test', defaults={'name': 'Export Test Type', 'is_active': True})

# Создаём активы
for i in range(3):
    Asset.objects.get_or_create(
        asset_tag='EXP{:03d}'.format(i),
        defaults={
            'name': 'Export Asset {}'.format(i),
            'asset_type': asset_type,
            'current_location': location,
            'status': 'available',
            'created_by': admin
        }
    )

client = APIClient()
client.force_authenticate(user=admin)

# Test CSV export
print('Testing CSV Export...')
resp = client.get('/api/reports/export/?format=csv')
print('Status:', resp.status_code)
if resp.status_code == 200:
    print('Content-Type:', resp.get('Content-Type', 'N/A'))
    print('Content-Disposition:', resp.get('Content-Disposition', 'N/A'))
    content = resp.content.decode('utf-8', errors='ignore')
    print('Data preview:')
    print(content[:500])
else:
    print('Error:', resp.content.decode())
