# AetherVane Aether Core Engine — Root URL Configuration
# =======================================================
# This file maps URLs to the code that handles them.
# Think of it as a directory in a building — when someone visits a URL,
# Django looks here to find which "room" (view) to send them to.

from django.contrib import admin
from django.urls import path, include

# Each entry in urlpatterns is like a signpost:
# "If someone visits this URL, send them to this code"

urlpatterns = [
    # /admin/ — Django's built-in admin panel (a ready-made management interface
    # where you can add/edit users, sites, devices, and data manually)
    path('admin/', admin.site.urls),
    
    # /api/v1/auth/ — User authentication (login, get JWT token, refresh token)
    # handled by the accounts app
    path('api/v1/auth/', include('accounts.urls')),
    
    # /api/v1/sites/ — Site and device management (CRUD operations)
    # CRUD = Create, Read, Update, Delete — the 4 basic operations on data
    path('api/v1/sites/', include('sites.urls')),
    
    # /api/v1/telemetry/ — Sensor data ingestion and retrieval
    # This is where the ESP32 sends its readings
    path('api/v1/telemetry/', include('telemetry.urls')),
]
