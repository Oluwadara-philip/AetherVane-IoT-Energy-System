"""
AetherVane — Test Data Setup Script
Creates: 1 organization, 1 site, 1 device, 4 circuits, 20 telemetry readings, 1 relay state
Run: python manage.py shell < create_test_data.py
or:  python manage.py shell -c "exec(open('create_test_data.py').read())"
"""
import uuid
import random
from django.utils import timezone
from datetime import timedelta

from sites.models import Organization, Site, Device, Circuit
from telemetry.models import PowerReading, RelayState

# Clean up existing test data
PowerReading.objects.all().delete()
RelayState.objects.all().delete()
Circuit.objects.all().delete()
Device.objects.all().delete()
Site.objects.all().delete()
Organization.objects.all().delete()

# Create organization
org = Organization.objects.create(name='Test Solar Farm')

# Create site
site = Site.objects.create(name='Main Building', organization=org, location='Rooftop Block A')

# Create device (using actual model fields)
device = Device.objects.create(
    name='Vane Node #1',
    site=site,
    mac_address='AA:BB:CC:DD:EE:FF',
    api_token=uuid.uuid4().hex,
    device_status='online',
)

# Create circuits (4 relay channels)
circuits = [
    ('Lights & Router', 1),
    ('Fans & TV', 2),
    ('Air Conditioner', 3),
    ('Water Heater', 4),
]
for i, (name, priority) in enumerate(circuits, 1):
    Circuit.objects.create(name=name, device=device, relay_number=i, priority=priority)

# Create initial relay state (all ON)
RelayState.objects.create(
    device=device,
    relay_1=True, relay_2=True, relay_3=True, relay_4=True,
    last_source='system'
)

# Create 20 sample telemetry readings (simulating voltage drop over time)
now = timezone.now()
for i in range(20):
    voltage = round(12.6 - (i * 0.05) + random.uniform(-0.1, 0.1), 2)
    current = round(random.uniform(1.5, 3.5), 2)
    wattage = round(voltage * current, 2)
    soc = round(((voltage - 10.5) / (12.6 - 10.5)) * 100, 1)
    PowerReading.objects.create(
        device=device,
        voltage=voltage,
        current=current,
        wattage=wattage,
        battery_pct=soc
    )

# Update device heartbeat
device.last_heartbeat = now
device.save()

print('Test data created successfully!')
print(f'  Organization: {org.name}')
print(f'  Site: {site.name} ({site.location})')
print(f'  Device: {device.name} [{device.mac_address}]')
print(f'  Circuits: {Circuit.objects.count()}')
print(f'  Power Readings: {PowerReading.objects.count()}')
print(f'  Relay State: {RelayState.objects.get(device=device)}')
print(f'\nAdmin login: username=admin  password=admin12345')
