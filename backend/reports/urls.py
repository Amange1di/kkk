from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, ReportSummaryViewSet

# Явные маршруты для AuditLogViewSet
audit_list = AuditLogViewSet.as_view({'get': 'list'})
audit_detail = AuditLogViewSet.as_view({'get': 'retrieve'})

# Явные маршруты для ReportSummaryViewSet
urlpatterns = [
    # Сначала audit-logs (чтобы не конфликтовать с пустым паттерном)
    path('audit-logs/', audit_list, name='audit-log-list'),
    path('audit-logs/<int:pk>/', audit_detail, name='audit-log-detail'),
    # Затем export и assets-summary (до пустого паттерна)
    path('export/', ReportSummaryViewSet.as_view({'get': 'export_data'}), name='report-export'),
    path('assets-summary/', ReportSummaryViewSet.as_view({'get': 'assets_summary'}), name='report-assets-summary'),
    # И только потом пустой паттерн для list
    path('', ReportSummaryViewSet.as_view({'get': 'list'}), name='report-list'),
]
