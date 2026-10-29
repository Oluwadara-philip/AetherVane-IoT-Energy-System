# AetherVane Telemetry App — Admin Registration

from django.contrib import admin
from .models import PowerReading, RelayState, AlertLog


@admin.register(PowerReading)
class PowerReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'voltage', 'current', 'wattage', 'battery_pct', 'timestamp')
    list_filter = ('device__site__organization', 'timestamp')
    search_fields = ('device__name', 'device__mac_address')


@admin.register(RelayState)
class RelayStateAdmin(admin.ModelAdmin):
    list_display = ('device', 'relay_1', 'relay_2', 'relay_3', 'relay_4', 'last_source', 'last_updated')
    list_filter = ('last_source',)


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'event_type', 'severity', 'description', 'created_at')
    list_filter = ('event_type', 'severity', 'created_at')
    search_fields = ('description',)
