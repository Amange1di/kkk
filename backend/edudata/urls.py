from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path as django_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/assets/", include("assets.urls")),
    path("api/locations/", include("locations.urls")),
    path("api/reports/", include("reports.urls")),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production
    urlpatterns += [
        from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/assets/", include("assets.urls")),
    path("api/locations/", include("locations.urls")),
    path("api/reports/", include("reports.urls")),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production
    urlpatterns += [
        path(r'^media/(?P<path>.*)
    ], serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    ]