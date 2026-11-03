"""Root URL configuration for boxsystem."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("packing.urls")),
]
