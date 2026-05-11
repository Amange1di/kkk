import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from reports.views import ReportSummaryViewSet

print('Methods in ReportSummaryViewSet:')
for attr in dir(ReportSummaryViewSet):
    if 'export' in attr.lower() or 'list' in attr.lower():
        print(' ', attr)

print()
print('Has export_data:', hasattr(ReportSummaryViewSet, 'export_data'))
print('Has list:', hasattr(ReportSummaryViewSet, 'list'))
print()
print('action_map:', getattr(ReportSummaryViewSet, 'action_map', 'N/A'))
