import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from accounts.models import CustomUser

# Create or update admin user
admin_user, created = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@edudata.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

if not created:
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True

admin_user.set_password('admin123')
admin_user.save()

print('Admin user created/updated successfully!')
print(f'Username: admin')
print(f'Password: admin123')
