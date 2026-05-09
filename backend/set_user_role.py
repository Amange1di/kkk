import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
import django
django.setup()

from accounts.models import CustomUser

print('Existing users:')
for user in CustomUser.objects.all():
    print(f'  {user.username} - role: {user.role}')

# Изменяем роль admin на inventory_manager
try:
    user = CustomUser.objects.get(username='admin')
    old_role = user.role
    user.role = 'inventory_manager'
    user.save()
    print(f'\nChanged {user.username} role from {old_role} to {user.role}')
except CustomUser.DoesNotExist:
    print('User "admin" not found')

# Создаем super_admin если нет
if not CustomUser.objects.filter(role='super_admin').exists():
    super_admin = CustomUser.objects.create_superuser(
        username='superadmin',
        email='superadmin@edudata.com',
        password='superadmin123',
        role='super_admin'
    )
    print(f'\nCreated super_admin user: {super_admin.username}')
else:
    print('\nSuper admin already exists')

print('\nUpdated users:')
for user in CustomUser.objects.all():
    print(f'  {user.username} - role: {user.role}')
