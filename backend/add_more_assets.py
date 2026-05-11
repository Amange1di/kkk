"""
Script to add more assets to reach 100 total
"""
import os
import sys
import django
from datetime import date, timedelta
from random import choice, randint, random

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from accounts.models import CustomUser
from locations.models import Location
from assets.models import AssetType, Asset, TransferHistory
from reports.models import AuditLog

def add_assets():
    print("=" * 60)
    print("Adding more assets to reach 100...")
    print("=" * 60)
    
    current_count = Asset.objects.count()
    print(f"\nCurrent assets: {current_count}")
    
    if current_count >= 100:
        print(f"  ✓ Already have {current_count} assets!")
        return
    
    target = 100
    to_create = target - current_count
    print(f"  Need to create: {to_create} more assets")
    
    # Get existing data
    users = list(CustomUser.objects.all())
    if not users:
        print("Error: No users found!")
        return
    
    asset_types = list(AssetType.objects.all())
    if not asset_types:
        print("Error: No asset types found!")
        return
    
    locations = list(Location.objects.filter(location_type='room'))
    if not locations:
        print("Error: No room locations found!")
        return
    
    departments = ['IT Department', 'HR Department', 'Finance', 'Academic', 'Administration', 'Library', 'Lab', 'Maintenance']
    statuses = ['available', 'in_use', 'in_repair', 'retired']
    
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
    
    super_admin = users[0]
    
    print(f"\nCreating {to_create} assets...")
    created = 0
    
    for i in range(current_count, target):
        asset_type = asset_types[i % len(asset_types)]
        asset_type_code = asset_type.code
        manufacturer = choice(manufacturers.get(asset_type_code, ['Generic']))
        model = choice(models_by_type.get(asset_type_code, ['Model']))
        
        year = date.today().year
        seq = str(i + 1).zfill(4)
        asset_tag = f'{year}-{asset_type_code[:3].upper()}-{seq}'
        
        # Skip if exists
        if Asset.objects.filter(asset_tag=asset_tag).exists():
            print(f"  ✓ Asset #{i+1} exists: {asset_tag}")
            created += 1
            continue
        
        status = choice(statuses)
        current_location = choice(locations) if status != 'retired' else None
        assigned_to = choice(users[1:]) if status == 'in_use' and len(users) > 1 else None
        
        purchase_date = date(2020 + (i % 5), randint(1, 12), randint(1, 28))
        warranty_expires = purchase_date + timedelta(days=randint(365, 5*365))
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
            auditor=f'Room {choice([l.room_number for l in locations])}' if current_location else None,
            auditor_user=choice(users[1:]) if current_location and len(users) > 1 else None,
            department=choice(departments),
            created_by=super_admin
        )
        created += 1
        print(f"  ✓ Created asset #{i+1}: {asset_tag} - {asset.name} ({status})")
    
    # Add transfer history for new assets
    print(f"\nAdding transfer history...")
    assets = Asset.objects.all()
    existing_transfers = TransferHistory.objects.values_list('asset_id', flat=True)
    assets_without_transfers = assets.exclude(id__in=existing_transfers)
    
    transfer_count = 0
    for asset in list(assets_without_transfers)[:20]:
        if asset.current_location:
            TransferHistory.objects.create(
                asset=asset,
                transfer_type=choice(['checkout', 'transfer', 'checkin']),
                to_location=asset.current_location,
                to_user=asset.assigned_to,
                reason='Initial assignment',
                performed_by=super_admin
            )
            transfer_count += 1
    
    print(f"  ✓ Created {transfer_count} transfer records")
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"  Total Assets: {Asset.objects.count()}")
    print(f"  Total Users: {CustomUser.objects.count()}")
    print(f"  Total Transfers: {TransferHistory.objects.count()}")
    print("=" * 60)

if __name__ == '__main__':
    add_assets()
