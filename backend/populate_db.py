"""
Script to populate the database with sample data (minimum 50 assets)
Run with: python manage.py populate_db
"""
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

def populate_db():
    print("=" * 60)
    print("Starting database population...")
    print("=" * 60)
    
    # Clear existing data (optional - only for clean start)
    print("\n[1/6] Preparing data...")
    # Comment out clearing to preserve existing data when adding more
    # TransferHistory.objects.all().delete()
    # Asset.objects.all().delete()
    # AssetType.objects.all().delete()
    # Location.objects.all().delete()
    # AuditLog.objects.all().delete()
    # CustomUser.objects.exclude(is_superuser=True).delete()
    
    current_asset_count = Asset.objects.count()
    print(f"  Current assets: {current_asset_count}")
    
    # Create Users
    print("\n[2/6] Creating users...")
    roles = [
        ('super_admin', 'Super Admin'),
        ('inventory_manager', 'Inventory Manager'),
        ('inventory_manager', 'Inventory Manager'),
        ('staff', 'Staff'),
        ('staff', 'Staff'),
        ('staff', 'Staff'),
        ('auditor', 'Auditor'),
        ('auditor', 'Auditor'),
    ]
    
    departments = ['IT Department', 'HR Department', 'Finance', 'Academic', 'Administration', 'Library', 'Lab', 'Maintenance']
    
    users = []
    
    # Create super admin
    if CustomUser.objects.filter(username='admin').exists():
        super_admin = CustomUser.objects.get(username='admin')
        print(f"  ✓ Using existing super admin: {super_admin.username}")
    else:
        super_admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@edudata.local',
            password='admin123',
            role='super_admin',
            department='Administration',
            phone='+7-XXX-XXX-0001'
        )
        print(f"  ✓ Created super admin: {super_admin.username}")
    users.append(super_admin)
    
    # Create regular users
    for i, (role, role_display) in enumerate(roles):
        username = f'user{i+1}'
        if CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.get(username=username)
            print(f"  ✓ Using existing user: {username} ({role_display})")
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=f'{username}@edudata.local',
                password='user123',
                role=role,
                department=choice(departments),
                phone=f'+7-XXX-XXX-{str(i+10).zfill(4)}'
            )
            print(f"  ✓ Created user: {username} ({role_display})")
        users.append(user)
    
    # Create Asset Types
    print("\n[3/6] Creating asset types...")
    asset_types_data = [
        ('Desktop Computer', 'desktop', 'Stationary desktop computers'),
        ('Laptop', 'laptop', 'Portable laptop computers'),
        ('Monitor', 'monitor', 'Computer monitors and displays'),
        ('Keyboard', 'keyboard', 'Computer keyboards'),
        ('Mouse', 'mouse', 'Computer mice'),
        ('Printer', 'printer', 'Printers and multifunction devices'),
        ('Tablet', 'tablet', 'Tablet devices'),
        ('Projector', 'projector', 'Video projectors'),
        ('Server', 'server', 'Server equipment'),
        ('Router', 'router', 'Network routers and switches'),
        ('Chair', 'chair', 'Office chairs'),
        ('Desk', 'desk', 'Office desks'),
        ('Filing Cabinet', 'filing_cabinet', 'Storage cabinets'),
        ('Whiteboard', 'whiteboard', 'Writing boards'),
        ('Telephone', 'telephone', 'Office telephones'),
    ]
    
    asset_types = {}
    for name, code, desc in asset_types_data:
        if AssetType.objects.filter(code=code).exists():
            at = AssetType.objects.get(code=code)
            print(f"  ✓ Using existing asset type: {name}")
        else:
            at = AssetType.objects.create(
                name=name,
                code=code,
                description=desc
            )
            print(f"  ✓ Created asset type: {name}")
        asset_types[code] = at
    
    # Create Locations
    print("\n[4/6] Creating locations...")
    
    # Main building
    if Location.objects.filter(name='Main Building').exists():
        main_building = Location.objects.get(name='Main Building')
        print(f"  ✓ Using existing location: {main_building.name}")
    else:
        main_building = Location.objects.create(
            name='Main Building',
            location_type='building',
            building='Main',
            address='123 University Street',
            description='Main academic building',
            is_active=True
        )
        print(f"  ✓ Created location: {main_building.name}")
    
    # Floors
    floors = {}
    for i in range(1, 4):
        floor_name = f'{i}st Floor' if i == 1 else f'{i}nd Floor' if i == 2 else f'{i}rd Floor'
        if Location.objects.filter(name=floor_name, parent_location=main_building).exists():
            floor = Location.objects.get(name=floor_name, parent_location=main_building)
            floors[i] = floor
            print(f"  ✓ Using existing location: {floor.name}")
        else:
            floor = Location.objects.create(
                name=floor_name,
                location_type='floor',
                parent_location=main_building,
                floor=str(i),
                is_active=True
            )
            floors[i] = floor
            print(f"  ✓ Created location: {floor.name}")
    
    # Rooms
    rooms = []
    room_configs = [
        (1, '101', 'office', 'IT Department'),
        (1, '102', 'office', 'HR Department'),
        (1, '103', 'office', 'Finance'),
        (1, '104', 'office', 'Administration'),
        (2, '201', 'room', 'Computer Lab 1'),
        (2, '202', 'room', 'Computer Lab 2'),
        (2, '203', 'room', 'Conference Room'),
        (2, '204', 'office', 'Academic Office'),
        (3, '301', 'room', 'Library'),
        (3, '302', 'room', 'Study Room'),
        (3, '303', 'office', 'Director Office'),
        (3, '304', 'warehouse', 'Storage Room'),
    ]
    
    for floor_num, room_num, loc_type, desc in room_configs:
        floor = floors[floor_num]
        if Location.objects.filter(name=f'Room {room_num}', parent_location=floor).exists():
            room = Location.objects.get(name=f'Room {room_num}', parent_location=floor)
            rooms.append(room)
            print(f"  ✓ Using existing location: {room.name}")
        else:
            room = Location.objects.create(
                name=f'Room {room_num}',
                location_type=loc_type,
                parent_location=floor,
                floor=str(floor_num),
                room_number=room_num,
                description=desc,
                capacity=randint(5, 50),
                is_active=True
            )
            rooms.append(room)
            print(f"  ✓ Created location: {room.name}")
    
    # Create Assets (50+)
    print("\n[5/6] Creating assets (50+)...")
    
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
    
    statuses = ['available', 'in_use', 'in_repair', 'retired']
    status_weights = [40, 45, 10, 5]
    
    assets_created = 0
    purchase_date = date(2020, 1, 1)
    
    # Get the next starting index based on existing assets
    existing_assets = Asset.objects.all()
    start_index = existing_assets.count()
    target_count = 100  # Target total assets
    
    if start_index >= target_count:
        print(f"  ✓ Already have {start_index} assets (target: {target_count})")
    else:
        print(f"\n[5/6] Creating assets (target: {target_count}, current: {start_index})...")
        
        for i in range(start_index, target_count):  # Create remaining assets to reach 100
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
            print(f"  ✓ Using existing asset: {asset.asset_tag} - {asset.name}")
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
            name=f'{asset_type.name} {i+1}',
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
            auditor=f'Room {choice([r.room_number for r in rooms])}' if current_location else None,
            auditor_user=choice(users[1:]) if current_location else None,
            department=choice(departments),
            created_by=super_admin
        )
        assets_created += 1
        print(f"  ✓ Created asset #{i+1}: {asset.asset_tag} - {asset.name} ({status})")
    
    print(f"\n  Total assets created: {assets_created}")
    
    # Create Transfer History (add more for new assets)
    print("\n[6/6] Creating transfer history...")
    transfers_created = 0
    
    assets = Asset.objects.all()
    # Create transfers for assets that don't have them yet
    existing_transfers = TransferHistory.objects.values_list('asset_id', flat=True)
    assets_without_transfers = assets.exclude(id__in=existing_transfers)
    
    for asset in list(assets_without_transfers)[:30]:
        if asset.current_location:
            transfer = TransferHistory.objects.create(
                asset=asset,
                transfer_type=choice(['checkout', 'transfer', 'checkin']),
                from_location=choice(rooms) if asset.status == 'in_use' else None,
                to_location=asset.current_location,
                from_user=None,
                to_user=asset.assigned_to,
                reason='Initial assignment',
                notes=f'Asset assigned to {asset.current_location.name}',
                performed_by=super_admin
            )
            transfers_created += 1
    
    print(f"  ✓ Created {transfers_created} transfer records")
    
    # Create Audit Logs
    print("\nCreating audit logs...")
    audit_logs_created = 0
    
    actions = ['create', 'update', 'login', 'scan', 'export']
    for i in range(20):
        log = AuditLog.objects.create(
            user=choice(users),
            action=choice(actions),
            model_name='Asset',
            object_id=str(randint(1, 60)),
            object_name=f'Asset #{randint(1, 60)}',
            ip_address=f'192.168.1.{randint(1, 254)}',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        )
        audit_logs_created += 1
    
    print(f"  ✓ Created {audit_logs_created} audit log entries")
    
    # Summary
    print("\n" + "=" * 60)
    print("DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    print(f"  Users: {CustomUser.objects.count()}")
    print(f"  Asset Types: {AssetType.objects.count()}")
    print(f"  Locations: {Location.objects.count()}")
    print(f"  Assets: {Asset.objects.count()}")
    print(f"  Transfer History: {TransferHistory.objects.count()}")
    print(f"  Audit Logs: {AuditLog.objects.count()}")
    print("=" * 60)
    print("\nDefault credentials:")
    print("  Admin: admin / admin123")
    print("  Users: user1-user8 / user123")
    print("=" * 60)

if __name__ == '__main__':
    populate_db()
