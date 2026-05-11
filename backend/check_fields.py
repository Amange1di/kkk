import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from assets.models import Asset, AssetType, TransferHistory
from locations.models import Location
from accounts.models import CustomUser

print("=" * 50)
print("Asset Model Fields:")
print("=" * 50)
for f in Asset._meta.get_fields():
    print(f"  - {f.name}: {type(f).__name__}")

print("\n" + "=" * 50)
print("AssetType Model:")
print("=" * 50)
print(f"  Exists: {AssetType._meta.label}")

print("\n" + "=" * 50)
print("Location Model Fields:")
print("=" * 50)
for f in Location._meta.get_fields():
    print(f"  - {f.name}: {type(f).__name__}")

print("\n" + "=" * 50)
print("CustomUser Model Fields:")
print("=" * 50)
for f in CustomUser._meta.get_fields():
    print(f"  - {f.name}: {type(f).__name__}")

print("\n" + "=" * 50)
print("Testing DB queries:")
print("=" * 50)
try:
    assets_count = Asset.objects.count()
    print(f"  Assets count: {assets_count}")
except Exception as e:
    print(f"  Asset query error: {e}")

try:
    locations_count = Location.objects.count()
    print(f"  Locations count: {locations_count}")
except Exception as e:
    print(f"  Location query error: {e}")

try:
    users_count = CustomUser.objects.count()
    print(f"  Users count: {users_count}")
except Exception as e:
    print(f"  User query error: {e}")

try:
    asset_types_count = AssetType.objects.count()
    print(f"  AssetTypes count: {asset_types_count}")
except Exception as e:
    print(f"  AssetType query error: {e}")