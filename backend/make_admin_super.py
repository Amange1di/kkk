import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
import django
django.setup()

from accounts.models import CustomUser

user = CustomUser.objects.get(username='admin')
user.role = 'super_admin'
user.save()
print(f'admin role changed to: {user.role}')
