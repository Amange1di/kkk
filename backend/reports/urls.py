from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, ReportSummaryViewSet, ReportExportViewSet

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'', ReportSummaryViewSet, basename='report-summary')
router.register(r'export', ReportExportViewSet, basename='report-export')

urlpatterns = [
    path('', include(router.urls)),
]
