import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from accounts.models import CustomUser

if not CustomUser.objects.filter(username='admin').exists():
    CustomUser.objects.create_superuser('admin', 'admin@edudata.com', 'admin123')
    print('Superuser "admin" created successfully!')
else:
    print('Superuser "admin" already exists.')
