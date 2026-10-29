# AetherVane Sites App — URL Routes
# ===================================
# Routes for organization, site, device, and circuit management.
# Included under /api/v1/sites/ (see aether_core/urls.py)

from django.urls import path
from .views import (
    OrganizationListCreateView, SiteListCreateView, SiteDetailView,
    DeviceListCreateView, DeviceDetailView, CircuitListCreateView
)

urlpatterns = [
    # Organizations
    path('organizations/', OrganizationListCreateView.as_view(), name='organization-list'),
    
    # Sites
    path('', SiteListCreateView.as_view(), name='site-list'),
    path('<int:site_id>/', SiteDetailView.as_view(), name='site-detail'),
    
    # Devices
    path('devices/', DeviceListCreateView.as_view(), name='device-list'),
    path('devices/<int:device_id>/', DeviceDetailView.as_view(), name='device-detail'),
    
    # Circuits (relay channel metadata)
    path('circuits/', CircuitListCreateView.as_view(), name='circuit-list'),
]
