# AetherVane Telemetry App — Serializers

from rest_framework import serializers
from .models import PowerReading, RelayState, AlertLog


class PowerReadingSerializer(serializers.ModelSerializer):
    """Serializer for telemetry ingestion from the ESP32."""
    
    class Meta:
        model = PowerReading
        fields = ['id', 'device', 'voltage', 'current', 'wattage', 'battery_pct', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class RelayStateSerializer(serializers.ModelSerializer):
    """Serializer for relay state data."""
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = RelayState
        fields = ['id', 'device', 'device_name', 'relay_1', 'relay_2', 'relay_3', 'relay_4',
                  'last_source', 'last_updated']
        read_only_fields = ['id', 'last_updated']


class AlertLogSerializer(serializers.ModelSerializer):
    """Serializer for alert/event log entries."""
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = AlertLog
        fields = ['id', 'device', 'device_name', 'event_type', 'severity',
                  'description', 'battery_pct_at_event', 'created_at']
        read_only_fields = ['id', 'created_at']


class TelemetryIngestSerializer(serializers.Serializer):
    """
    Serializer for the telemetry ingestion endpoint.
    
    This is what the ESP32 sends when it posts to /api/v1/telemetry/ingest/:
    {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "voltage": 12.3,
        "current": 2.5,
        "wattage": 30.75,
        "battery_pct": 85.0,
        "relay_states": [true, true, true, true]
    }
    
    The server validates this data, looks up the device by MAC address,
    stores the reading, runs the DSL engine, and returns updated relay states.
    """
    mac_address = serializers.CharField(max_length=20)
    voltage = serializers.FloatField()
    current = serializers.FloatField()
    wattage = serializers.FloatField()
    battery_pct = serializers.FloatField()
    relay_states = serializers.ListField(
        child=serializers.BooleanField(),
        min_length=4,
        max_length=4,
        required=False,
        default=[True, True, True, True]
    )
