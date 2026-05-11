import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from accounts.models import CustomUser
from reports.views import ReportSummaryViewSet

# Создаём тестовые данные
admin = CustomUser.objects.get(username='test_admin')

# Создаём запрос напрямую к view
factory = APIRequestFactory()
request = factory.get('/api/reports/export/?format=csv')
request.user = admin

view = ReportSummaryViewSet.as_view({'get': 'export_data'})
response = view(request)

print('Direct View Test:')
print('Status:', response.status_code)
if hasattr(response, 'content'):
    print('Content-Type:', response.get('Content-Type', 'N/A'))
    print('Content:', response.content[:500] if response.content else 'Empty')
else:
    print('Response data:', response.data if hasattr(response, 'data') else response)
