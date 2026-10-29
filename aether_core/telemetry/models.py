# AetherVane Telemetry App — Models
# ===================================
# This file defines the database tables for sensor data, relay states, and alerts.
#
# WHAT THIS FILE DEFINES (plain language):
#   1. PowerReading — Every time the ESP32 sends sensor data (voltage, current, etc.),
#      one row is added to this table. Like a diary entry: "At 3:05 PM, the battery
#      was at 12.3V, drawing 2.5A, total 30.75W, battery 85% full."
#   2. RelayState — Tracks which relays are currently ON or OFF. Updated whenever
#      the DSL engine changes relay states or a user manually overrides.
#   3. AlertLog — A record of important events: "Battery dropped below 25%, cut
#      Relay 3" or "User manually turned Relay 4 back on."

from django.db import models
from sites.models import Device


class PowerReading(models.Model):
    """
    A single telemetry reading from a Vane Node.
    
    Each row = one "snapshot" of the electrical system at a moment in time.
    The ESP32 sends one of these every 3 seconds (configurable).
    
    Fields:
      voltage   — Battery voltage in volts (e.g., 12.3)
      current   — Current flowing in amps (e.g., 2.5)
      wattage   — Power = voltage x current (e.g., 30.75W)
      battery_pct — Battery State of Charge as percentage (e.g., 85.0)
      timestamp  — When this reading was received
    
    This is a "time-series" table — it grows over time and we query it
    to draw charts ("show me the last 24 hours of voltage data").
    """
    
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='power_readings'
    )
    voltage = models.FloatField()
    current = models.FloatField()
    wattage = models.FloatField()
    battery_pct = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'power_readings'
        ordering = ['-timestamp']  # Newest first when querying
    
    def __str__(self):
        return "[{}] {}V / {}A / {}W / {}%".format(
            self.timestamp, self.voltage, self.current, self.wattage, self.battery_pct
        )


class RelayState(models.Model):
    """
    Current state of all 4 relays on a device.
    
    One row per device (updated in place, not appended like PowerReading).
    Each relay_X field is a Boolean (True = ON, False = OFF).
    
    When the DSL engine decides to cut a relay, it updates this table.
    When a user manually toggles a relay in the web dashboard, it updates this table.
    The ESP32 reads this (via the telemetry response) to know what to do.
    """
    
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name='relay_state'
    )
    relay_1 = models.BooleanField(default=True)  # Essential
    relay_2 = models.BooleanField(default=True)  # Secondary
    relay_3 = models.BooleanField(default=True)  # Heavy
    relay_4 = models.BooleanField(default=True)  # Extra Heavy
    last_updated = models.DateTimeField(auto_now=True)
    
    # Track WHY the relay states changed — was it automatic (DSL) or manual?
    SOURCE_CHOICES = [
        ('system', 'System Default'),
        ('dsl', 'DSL Auto-Shed'),
        ('manual', 'Manual Override'),
    ]
    last_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='system')
    
    class Meta:
        db_table = 'relay_states'
    
    def __str__(self):
        return "{}: R1={} R2={} R3={} R4={}".format(
            self.device.name, self.relay_1, self.relay_2, self.relay_3, self.relay_4
        )
    
    def as_list(self):
        """Return relay states as a list of booleans: [R1, R2, R3, R4]."""
        return [self.relay_1, self.relay_2, self.relay_3, self.relay_4]
    
    def update_from_list(self, states, source='dsl'):
        """Update relay states from a list [True, True, False, False]."""
        self.relay_1 = states[0]
        self.relay_2 = states[1]
        self.relay_3 = states[2]
        self.relay_4 = states[3]
        self.last_source = source
        self.save()


class AlertLog(models.Model):
    """
    A log entry for important events.
    
    This is the system's "event journal" — every time something notable happens,
    an entry is created here:
    - DSL triggers a relay cut: "Stage 1 shedding: cut Relay 4 (SoC 38%)"
    - User manually overrides: "User admin toggled Relay 3 OFF"
    - Battery recovers: "Battery recovered to 50%, re-engaging Relay 4"
    - Device goes offline: "No telemetry from device for 5 minutes"
    
    The web dashboard shows these in a scrolling alert feed.
    """
    
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('shedding', 'Load Shedding Event'),
        ('recovery', 'Battery Recovery'),
        ('manual_override', 'Manual Override'),
        ('device_offline', 'Device Offline'),
        ('device_online', 'Device Online'),
        ('threshold_breach', 'Threshold Breach'),
    ]
    
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='alert_logs'
    )
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    description = models.TextField()
    battery_pct_at_event = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alert_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return "[{}] {} - {}".format(self.created_at, self.event_type, self.description[:50])
