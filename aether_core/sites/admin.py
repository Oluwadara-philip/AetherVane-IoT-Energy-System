# AetherVane Sites App — Admin Registration

from django.contrib import admin
from .models import Organization, Site, Device, Circuit


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'location', 'is_active')
    list_filter = ('organization', 'is_active')
    search_fields = ('name', 'location')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'mac_address', 'site', 'device_status', 'last_heartbeat')
    list_filter = ('device_status', 'site__organization')
    search_fields = ('name', 'mac_address')


@admin.register(Circuit)
class CircuitAdmin(admin.ModelAdmin):
    list_display = ('device', 'relay_number', 'name', 'priority')
    list_filter = ('relay_number',)
