import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver,.onrender.com')

import django
django.setup()

from django.urls import reverse

try:
    url = reverse('assettype-list')
    print(f'assettype-list: {url}')
except Exception as e:
    print(f'assettype-list: Error - {e}')

try:
    url = reverse('transfer-list')
    print(f'transfer-list: {url}')
except Exception as e:
    print(f'transfer-list: Error - {e}')

try:
    url = reverse('public-asset-scan')
    print(f'public-asset-scan: {url}')
except Exception as e:
    print(f'public-asset-scan: Error - {e}')

try:
    url = reverse('asset-list')
    print(f'asset-list: {url}')
except Exception as e:
    print(f'asset-list: Error - {e}')
