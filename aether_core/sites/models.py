# AetherVane Sites App — Models
# ================================
# This file defines the database tables for the multi-tenant hierarchy:
#   Organization -> Site -> Device -> Circuit
#
# MULTI-TENANCY EXPLAINED (plain language):
# "Multi-tenant" means one system serves multiple independent customers
# (organizations), and each customer can only see their own data.
#
# ANALOGY: Think of an apartment building:
#   - The building = the AetherVane platform
#   - Each apartment = an Organization (one tenant company)
#   - Rooms in the apartment = Sites (physical locations)
#   - Appliances in rooms = Devices (ESP32 units)
#
# Just like apartment 3A's tenant can't enter apartment 3B,
# Organization A's users can't see Organization B's data.
# This isolation is enforced at the DATABASE LEVEL, not just the frontend.

from django.db import models
from django.conf import settings


class Organization(models.Model):
    """
    An Organization is the top level of the multi-tenant hierarchy.
    
    Each organization represents an independent customer — like a company
    that manages energy across multiple physical sites.
    
    Example: "Green Solar Farms Ltd" is an organization that has 3 sites:
    - Site 1: Factory building
    - Site 2: Office building  
    - Site 3: Warehouse
    """
    
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'organizations'  # Custom table name in MySQL
    
    def __str__(self):
        return self.name


class Site(models.Model):
    """
    A Site is a physical location where energy is monitored.
    
    Each site belongs to an Organization. A site has one or more
    Vane Node devices installed.
    
    Example: "Factory Building" is a site under "Green Solar Farms Ltd"
    """
    
    # organization: which org this site belongs to (FK = foreign key = link)
    # on_delete=models.CASCADE means: if the org is deleted, delete its sites too.
    # This prevents "orphan" sites without an owner.
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='sites'
    )
    
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sites'
    
    def __str__(self):
        return "{} ({})".format(self.name, self.organization.name)


class Device(models.Model):
    """
    A Device is a physical Vane Node (ESP32 + sensors + relays).
    
    Each device is registered to a specific site. The device's MAC address
    is used for authentication — when the ESP32 sends telemetry, the server
    checks the MAC against this table to verify the device is registered.
    
    The API token field is an additional security layer — the ESP32 must
    send this token in the Authorization header for its data to be accepted.
    """
    
    DEVICE_STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
    ]
    
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    
    # name: human-friendly name like "Vane Node #1 - Main Panel"
    name = models.CharField(max_length=200, default='Vane Node')
    
    # mac_address: the ESP32's unique hardware ID (from factory)
    # Used for device authentication — we match incoming data's MAC against this.
    mac_address = models.CharField(max_length=20, unique=True)
    
    # api_token: a secret string the device must send with each request.
    # Think of it as a password for the device (different from user passwords).
    api_token = models.CharField(max_length=64, blank=True, default='')
    
    device_status = models.CharField(
        max_length=20,
        choices=DEVICE_STATUS_CHOICES,
        default='offline'
    )
    
    # last_heartbeat: the last time the device sent data.
    # If this is old (e.g., > 5 minutes), the device is considered offline.
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'devices'
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.mac_address)


class Circuit(models.Model):
    """
    A Circuit represents one relay channel on a device.
    
    Each Vane Node has 4 relay channels, each controlling a group of appliances.
    By storing circuit metadata in the database, the web dashboard can show
    meaningful names (like "Air Conditioner") instead of just "Relay 3".
    
    The priority field determines which circuit gets cut first during load shedding:
      priority 1 = Essential (never cut)
      priority 2 = Secondary (cut second)
      priority 3 = Heavy (cut first)
      priority 4 = Extra Heavy (cut first)
    
    Note: lower number = more important = cut later.
    The DSL engine uses this to decide the shedding order.
    """
    
    RELAY_CHOICES = [
        (1, 'Relay 1'),
        (2, 'Relay 2'),
        (3, 'Relay 3'),
        (4, 'Relay 4'),
    ]
    
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='circuits'
    )
    
    relay_number = models.IntegerField(choices=RELAY_CHOICES)
    name = models.CharField(max_length=200, default='Circuit')
    description = models.TextField(blank=True, default='')
    priority = models.IntegerField(default=4)  # 1=highest priority (never cut), 4=lowest (cut first)
    
    class Meta:
        db_table = 'circuits'
        # A device can only have one circuit per relay number
        unique_together = ('device', 'relay_number')
    
    def __str__(self):
        return "{} - Relay {} ({})".format(self.device.name, self.relay_number, self.name)
