import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
import django
django.setup()

from accounts.models import CustomUser
print('Users:', list(CustomUser.objects.values_list('username', 'is_active')))
