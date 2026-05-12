"""
Script to update user names to Kyrgyz names
Run with: python manage.py update_kyrgyz_names
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from accounts.models import CustomUser

def update_kyrgyz_names():
    print("=" * 60)
    print("Обновление имён пользователей на кыргызские...")
    print("=" * 60)
    
    # Kyrgyz names for users
    kyrgyz_names = {
        'user1': ('Айбек', 'Абдыраимов'),
        'user2': ('Айгуль', 'Усубалиева'),
        'user3': ('Бакыт', 'Сарыбаев'),
        'user4': ('Гульнара', 'Касымалиева'),
        'user5': ('Данияр', 'Токтоналиев'),
        'user6': ('Эльвина', 'Мамытова'),
        'user7': ('Рустам', 'Исаев'),
        'user8': ('Айпери', 'Асанова'),
    }
    
    updated_count = 0
    
    for username, (first_name, last_name) in kyrgyz_names.items():
        try:
            user = CustomUser.objects.get(username=username)
            old_name = f"{user.first_name} {user.last_name}".strip()
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print(f"  ✓ Обновлён пользователь {username}: {old_name} → {first_name} {last_name}")
            updated_count += 1
        except CustomUser.DoesNotExist:
            print(f"  ⚠ Пользователь {username} не найден")
    
    print("\n" + "=" * 60)
    print(f"ОБНОВЛЕНО ПОЛЬЗОВАТЕЛЕЙ: {updated_count}")
    print("=" * 60)
    
    # Show all users
    print("\nВсе пользователи:")
    for user in CustomUser.objects.all().order_by('username'):
        print(f"  - {user.username}: {user.first_name} {user.last_name} ({user.get_role_display()})")

if __name__ == '__main__':
    update_kyrgyz_names()