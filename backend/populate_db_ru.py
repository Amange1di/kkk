'''
Script to populate the database with RUSSIAN sample data (minimum 50 assets)
Run with: python manage.py populate_db_ru
'''
import os
import sys
import django
from datetime import date, timedelta
from random import choice, randint, random

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from accounts.models import CustomUser
from locations.models import Location
from assets.models import AssetType, Asset, TransferHistory
from reports.models import AuditLog

def populate_db_ru():
    print("=" * 60)
    print("Начало заполнения базы данных русскими данными...")
    print("=" * 60)
    
    # Create Users with Russian names
    print("\n[1/6] Создание пользователей...")
    roles = [
        ('super_admin', 'Супер администратор'),
        ('inventory_manager', 'Менеджер по учёту'),
        ('inventory_manager', 'Менеджер по учёту'),
        ('staff', 'Сотрудник'),
        ('staff', 'Сотрудник'),
        ('staff', 'Сотрудник'),
        ('auditor', 'Аудитор'),
        ('auditor', 'Аудитор'),
    ]
    
    departments = ['Отдел информационных технологий', 'Отдел кадров', 'Бухгалтерия', 'Учебный отдел', 'Администрация', 'Библиотека', 'Лаборатория', 'Хозяйственный отдел']
    
    users = []
    
    # Create super admin
    if CustomUser.objects.filter(username='admin').exists():
        super_admin = CustomUser.objects.get(username='admin')
        print(f"  ✓ Используем существующего супер администратора: {super_admin.username}")
    else:
        super_admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@edudata.local',
            password='admin123',
            role='super_admin',
            department='Администрация',
            phone='+7-XXX-XXX-0001'
        )
        print(f"  ✓ Создан супер администратор: {super_admin.username}")
    users.append(super_admin)
    
    # Create regular users with Kyrgyz names
    kyrgyz_names = [
        ('Айбек', 'Абдыраимов'), ('Айгуль', 'Усубалиева'), ('Бакыт', 'Сарыбаев'),
        ('Гульнара', 'Касымалиева'), ('Данияр', 'Токтоналиев'), ('Эльвина', 'Мамытова'),
        ('Рустам', 'Исаев'), ('Айпери', 'Асанова')
    ]
    
    for i, (role, role_display) in enumerate(roles):
        username = f'user{i+1}'
        if CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.get(username=username)
            print(f"  ✓ Используем существующего пользователя: {username} ({role_display})")
        else:
            first_name, last_name = kyrgyz_names[i] if i < len(kyrgyz_names) else ('Колум', f'{i+1}')
            user = CustomUser.objects.create_user(
                username=username,
                email=f'{username}@edudata.local',
                password='user123',
                role=role,
                department=choice(departments),
                phone=f'+996-XXX-XXX-{str(i+10).zfill(4)}',
                first_name=first_name,
                last_name=last_name
            )
            print(f"  ✓ Создан пользователь: {first_name} {last_name} ({role_display})")
        users.append(user)
    
    # Create Asset Types in Russian
    print("\n[2/6] Создание типов активов...")
    asset_types_data = [
        ('Настольный компьютер', 'desktop', 'Стационарные настольные компьютеры'),
        ('Ноутбук', 'laptop', 'Портативные ноутбуки'),
        ('Монитор', 'monitor', 'Компьютерные мониторы и дисплеи'),
        ('Клавиатура', 'keyboard', 'Компьютерные клавиатуры'),
        ('Мышь', 'mouse', 'Компьютерные мыши'),
        ('Принтер', 'printer', 'Принтеры и многофункциональные устройства'),
        ('Планшет', 'tablet', 'Планшетные устройства'),
        ('Проектор', 'projector', 'Видеопроекторы'),
        ('Сервер', 'server', 'Серверное оборудование'),
        ('Роутер', 'router', 'Сетевые маршрутизаторы и коммутаторы'),
        ('Стул', 'chair', 'Офисные стулья'),
        ('Стол', 'desk', 'Офисные столы'),
        ('Шкаф для файлов', 'filing_cabinet', 'Хранение документов'),
        ('Доска для записей', 'whiteboard', 'Писчие доски'),
        ('Телефон', 'telephone', 'Офисные телефоны'),
    ]
    
    asset_types = {}
    for name, code, desc in asset_types_data:
        if AssetType.objects.filter(code=code).exists():
            at = AssetType.objects.get(code=code)
            print(f"  ✓ Используем существующий тип актива: {name}")
        else:
            at = AssetType.objects.create(
                name=name,
                code=code,
                description=desc
            )
            print(f"  ✓ Создан тип актива: {name}")
        asset_types[code] = at
    
    # Create Locations in Russian
    print("\n[3/6] Создание локаций...")
    
    # Main building
    if Location.objects.filter(name='Главный корпус').exists():
        main_building = Location.objects.get(name='Главный корпус')
        print(f"  ✓ Используем существующую локацию: {main_building.name}")
    else:
        main_building = Location.objects.create(
            name='Главный корпус',
            location_type='building',
            building='Главный',
            address='ул. Университетская, д. 123',
            description='Основное учебное здание',
            is_active=True
        )
        print(f"  ✓ Создана локация: {main_building.name}")
    
    # Floors
    floors = {}
    floor_names = ['1 этаж', '2 этаж', '3 этаж']
    for i, floor_name in enumerate(floor_names):
        if Location.objects.filter(name=floor_name, parent_location=main_building).exists():
            floor = Location.objects.get(name=floor_name, parent_location=main_building)
            floors[i+1] = floor
            print(f"  ✓ Используем существующую локацию: {floor.name}")
        else:
            floor = Location.objects.create(
                name=floor_name,
                location_type='floor',
                parent_location=main_building,
                floor=str(i+1),
                is_active=True
            )
            floors[i+1] = floor
            print(f"  ✓ Создана локация: {floor.name}")
    
    # Rooms
    rooms = []
    room_configs = [
        (1, '101', 'office', 'Отдел информационных технологий'),
        (1, '102', 'office', 'Отдел кадров'),
        (1, '103', 'office', 'Бухгалтерия'),
        (1, '104', 'office', 'Администрация'),
        (2, '201', 'room', 'Компьютерный класс 1'),
        (2, '202', 'room', 'Компьютерный класс 2'),
        (2, '203', 'room', 'Конференц-зал'),
        (2, '204', 'office', 'Учебный отдел'),
        (3, '301', 'room', 'Библиотека'),
        (3, '302', 'room', 'Кабинет для занятий'),
        (3, '303', 'office', 'Кабинет директора'),
        (3, '304', 'warehouse', 'Складское помещение'),
    ]
    
    for floor_num, room_num, loc_type, desc in room_configs:
        floor = floors[floor_num]
        room_name = f'Кабинет {room_num}'
        if Location.objects.filter(name=room_name, parent_location=floor).exists():
            room = Location.objects.get(name=room_name, parent_location=floor)
            rooms.append(room)
            print(f"  ✓ Используем существующую локацию: {room.name}")
        else:
            room = Location.objects.create(
                name=room_name,
                location_type=loc_type,
                parent_location=floor,
                floor=str(floor_num),
                room_number=room_num,
                description=desc,
                capacity=randint(5, 50),
                is_active=True
            )
            rooms.append(room)
            print(f"  ✓ Создана локация: {room.name}")
    
    # Create Assets in Russian (50+)
    print("\n[4/6] Создание активов (50+)...")
    
    manufacturers = {
        'desktop': ['Dell', 'HP', 'Lenovo', 'Acer'],
        'laptop': ['Dell', 'HP', 'Lenovo', 'Apple', 'Asus'],
        'monitor': ['Samsung', 'LG', 'Dell', 'HP'],
        'keyboard': ['Logitech', 'Dell', 'HP', 'Corsair'],
        'mouse': ['Logitech', 'Dell', 'HP', 'Razer'],
        'printer': ['HP', 'Canon', 'Epson', 'Brother'],
        'tablet': ['Apple', 'Samsung', 'Lenovo'],
        'projector': ['Epson', 'Canon', 'Sony'],
        'server': ['Dell', 'HP', 'Lenovo'],
        'router': ['Cisco', 'TP-Link', 'D-Link'],
        'chair': ['IKEA', 'Steelcase', 'Herman Miller'],
        'desk': ['IKEA', 'Steelcase', 'Herman Miller'],
        'filing_cabinet': ['IKEA', 'Steelcase', 'HON'],
        'whiteboard': ['Quartet', 'Expo', 'Griffin'],
        'telephone': ['Panasonic', 'Cisco', 'Avaya'],
    }
    
    models_by_type = {
        'desktop': ['OptiPlex 7090', 'ProDesk 400', 'ThinkCentre M70', 'Aspire TC'],
        'laptop': ['Latitude 5000', 'EliteBook 800', 'ThinkPad T14', 'MacBook Pro', 'VivoBook'],
        'monitor': ['S2721DS', '27UD69', 'P2722H', '27er'],
        'keyboard': ['MX Keys', 'KB280', 'EliteKeyboard', 'K552'],
        'mouse': ['MX Master 3', 'M720', 'EliteMouse', 'V500'],
        'printer': ['LaserJet Pro', 'OfficeJet Pro', 'WorkForce', 'MFC-L2700'],
        'tablet': ['iPad Air', 'Galaxy Tab', 'Tab P11'],
        'projector': ['EH-TW7100', 'X500', 'VPL-FW41'],
        'server': ['PowerEdge R740', 'ProLiant DL380', 'ThinkSystem SR650'],
        'router': ['ISR 4000', 'Archer AX50', 'DIR-882'],
        'chair': ['MARKUS', 'Aeron', 'Embody'],
        'desk': ['BEKANT', 'Aeron Desk', 'Renewed Standing Desk'],
        'filing_cabinet': ['ALEX', 'Tanner', 'Executive File Cabinet'],
        'whiteboard': ['Quartet Infinity', 'Expo Board', 'Griffin Glass Board'],
        'telephone': ['KX-T7750', '8845', 'IP Phone 7940'],
    }
    
    status_choices = {
        'available': 'Доступен',
        'in_use': 'В использовании',
        'in_repair': 'В ремонте',
        'retired': 'Списан',
        'lost': 'Потерян'
    }
    
    statuses = ['available', 'in_use', 'in_repair', 'retired']
    status_weights = [40, 45, 10, 5]
    
    assets_created = 0
    purchase_date = date(2020, 1, 1)
    
    # Get the next starting index based on existing assets
    existing_assets = Asset.objects.all()
    start_index = existing_assets.count()
    target_count = 100  # Target total assets
    
    if start_index >= target_count:
        print(f"  ✓ Уже есть {start_index} активов (цель: {target_count})")
    else:
        print(f"\n[4/6] Создание активов (цель: {target_count}, текущее: {start_index})...")
        
        for i in range(start_index, target_count):
            asset_type_code = list(asset_types.keys())[i % len(asset_types.keys())]
            asset_type = asset_types[asset_type_code]
            manufacturer = choice(manufacturers[asset_type_code])
            model = choice(models_by_type[asset_type_code])
            
            # Generate asset tag
            year = date.today().year
            seq = str(i + 1).zfill(4)
            asset_tag = f'{year}-{asset_type_code[:3].upper()}-{seq}'
            
            # Check if asset already exists
            if Asset.objects.filter(asset_tag=asset_tag).exists():
                asset = Asset.objects.get(asset_tag=asset_tag)
                assets_created += 1
                print(f"  ✓ Используем существующий актив: {asset.asset_tag} - {asset.name}")
                continue
            
            # Random status with weights
            status = choice(statuses)
            
            # Random location
            current_location = choice(rooms) if status != 'retired' else None
            
            # Assigned user
            assigned_to = choice(users[1:]) if status == 'in_use' else None
            
            # Calculate dates
            purchase_date = date(2020 + (i % 5), randint(1, 12), randint(1, 28))
            warranty_years = randint(1, 5)
            warranty_expires = purchase_date + timedelta(days=warranty_years * 365)
            
            assigned_date = purchase_date + timedelta(days=randint(30, 365)) if assigned_to else None
            
            asset = Asset.objects.create(
                asset_tag=asset_tag,
                name=f'{asset_type.name} №{i+1}',
                description=f'{manufacturer} {model} - {asset_type.description}',
                asset_type=asset_type,
                manufacturer=manufacturer,
                model=model,
                serial_number=f'{manufacturer[:2].upper()}{randint(100000, 999999)}',
                purchase_date=purchase_date,
                warranty_expires=warranty_expires,
                purchase_price=round(randint(5000, 150000) + random(), 2),
                currency='RUB',
                status=status,
                current_location=current_location,
                assigned_to=assigned_to,
                assigned_date=assigned_date,
                auditor=f'Кабинет {choice([r.room_number for r in rooms])}' if current_location else None,
                auditor_user=choice(users[1:]) if current_location else None,
                department=choice(departments),
                created_by=super_admin
            )
            assets_created += 1
            status_ru = status_choices[status]
            print(f"  ✓ Создан актив #{i+1}: {asset.asset_tag} - {asset.name} ({status_ru})")
    
    print(f"\n  Всего создано активов: {assets_created}")
    
    # Create Transfer History
    print("\n[5/6] Создание истории перемещений...")
    transfers_created = 0
    
    assets = Asset.objects.all()
    existing_transfers = TransferHistory.objects.values_list('asset_id', flat=True)
    assets_without_transfers = assets.exclude(id__in=existing_transfers)
    
    transfer_types = {
        'checkout': 'Выдача',
        'checkin': 'Возврат',
        'transfer': 'Перемещение',
        'maintenance': 'Обслуживание',
        'return': 'Возврат'
    }
    
    for asset in list(assets_without_transfers)[:30]:
        if asset.current_location:
            transfer_type = choice(['checkout', 'transfer', 'checkin'])
            transfer = TransferHistory.objects.create(
                asset=asset,
                transfer_type=transfer_type,
                from_location=choice(rooms) if asset.status == 'in_use' else None,
                to_location=asset.current_location,
                from_user=None,
                to_user=asset.assigned_to,
                reason='Первоначальное закрепление',
                notes=f'Актив закреплен за {asset.current_location.name}',
                performed_by=super_admin
            )
            transfers_created += 1
    
    print(f"  ✓ Создано {transfers_created} записей о перемещении")
    
    # Create Audit Logs
    print("\n[6/6] Создание журналов аудита...")
    audit_logs_created = 0
    
    action_choices = {
        'create': 'Создание',
        'update': 'Обновление',
        'delete': 'Удаление',
        'login': 'Вход',
        'logout': 'Выход',
        'scan': 'Сканирование QR',
        'export': 'Экспорт',
        'transfer': 'Перемещение',
        'checkout': 'Выдача',
        'checkin': 'Возврат'
    }
    
    actions = ['create', 'update', 'login', 'scan', 'export']
    for i in range(20):
        log = AuditLog.objects.create(
            user=choice(users),
            action=choice(actions),
            model_name='Asset',
            object_id=str(randint(1, 100)),
            object_name=f'Актив #{randint(1, 100)}',
            ip_address=f'192.168.1.{randint(1, 254)}',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        )
        audit_logs_created += 1
    
    print(f"  ✓ Создано {audit_logs_created} записей журнала аудита")
    
    # Summary
    print("\n" + "=" * 60)
    print("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ ЗАВЕРШЕНО!")
    print("=" * 60)
    print(f"  Пользователи: {CustomUser.objects.count()}")
    print(f"  Типы активов: {AssetType.objects.count()}")
    print(f"  Локации: {Location.objects.count()}")
    print(f"  Активы: {Asset.objects.count()}")
    print(f"  История перемещений: {TransferHistory.objects.count()}")
    print(f"  Журналы аудита: {AuditLog.objects.count()}")
    print("=" * 60)
    print("\nУчётные данные по умолчанию:")
    print("  Администратор: admin / admin123")
    print("  Пользователи: user1-user8 / user123")
    print("=" * 60)

if __name__ == '__main__':
    populate_db_ru()