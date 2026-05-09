import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
import django
django.setup()

from django.test import Client, override_settings
import json

with override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1']):
    c = Client()
    data = json.dumps({'username': 'admin', 'password': 'admin123'})
    r = c.post('/api/accounts/login/', data, content_type='application/json')
    print('Status:', r.status_code)
    if r.status_code == 200:
        print('Response:', r.json())
    else:
        print('Response:', r.content.decode())
