import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from django.urls import resolve, get_resolver
resolver = get_resolver()

# Проверка разрешения URL
try:
    match = resolver.resolve('/api/reports/export/')
    print('Resolved /api/reports/export/:', match.func, match.url_name)
except Exception as e:
    print('Not resolved /api/reports/export/:', e)

try:
    match = resolver.resolve('/api/reports/assets-summary/')
    print('Resolved /api/reports/assets-summary/:', match.func, match.url_name)
except Exception as e:
    print('Not resolved /api/reports/assets-summary/:', e)
