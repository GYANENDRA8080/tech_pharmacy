from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pharmacy.admin import developer_admin

urlpatterns = [
    path("admin/", developer_admin.urls),  # Use custom developer-only admin
    path("", include("pharmacy.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
