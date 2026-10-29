# AetherVane Vane Node — Configuration File
# ============================================
# This file holds all the settings the Vane Node needs to operate.
# Think of it as the "ID card" for this device — it tells the ESP32
# who it is, where to connect, and which pins everything is wired to.

# --- Wi-Fi Settings ---
# These are the name and password of the Wi-Fi network the ESP32 will connect to.
# SSID = the Wi-Fi network name you see when you scan for networks on your phone.
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# --- Cloud Server Settings ---
# This is the web address of our Django backend (the "Aether Core Engine").
# During development, this will be your computer's local IP address.
# SERVER_URL = "http://192.168.1.100:8000"  # <-- Replace with your PC's IP
SERVER_URL = "http://192.168.1.100:8000"

# The specific endpoint (like a specific door at an address) where we send sensor data.
# The ESP32 sends a POST request here with the sensor readings.
TELEMETRY_ENDPOINT = "/api/v1/telemetry/ingest/"

# The endpoint where we fetch the latest relay commands (what switches should be on/off).
RELAY_COMMAND_ENDPOINT = "/api/v1/telemetry/relay-states/"

# --- Device Identity ---
# This token is like a password for the device. The cloud server checks this
# to make sure the data is coming from a real, registered Vane Node — not a fake.
# You'll get this token when you register the device in the Django backend.
DEVICE_TOKEN = "PLACEHOLDER_REPLACE_AFTER_DEVICE_REGISTRATION"

# The MAC address is a unique hardware ID burned into every ESP32 at the factory.
# No two ESP32 chips have the same MAC address — like a fingerprint.
# We'll read this automatically in the code, but you can also hardcode it here.
# DEVICE_MAC = "AA:BB:CC:DD:EE:FF"

# --- Sensor Pin Assignments ---
# The ESP32 has numbered pins (like numbered outlets on a power strip).
# These tell the code which pins the sensors are wired to.
#
# ADC = "Analog-to-Digital Converter" — a pin that can read varying voltages
# (not just ON/OFF, but a range like 0 to 3.3 volts). This is what we need
# for sensors that measure a continuous value like voltage or current.
#
# On the ESP32, ADC pins are numbered ADC1_0 through ADC1_5 (GPIO 32-39).
# We avoid ADC2 pins because they stop working when Wi-Fi is on (a known ESP32 quirk).

# Pin that reads voltage from the voltage divider circuit
VOLTAGE_SENSOR_PIN = 34  # ADC1_CH6 — reads the battery voltage (via divider)

# Pin that reads current from the CT clamp sensor
CURRENT_SENSOR_PIN = 35  # ADC1_CH7 — reads the current sensor output

# --- Relay Pin Assignments ---
# These are the GPIO (General Purpose Input/Output) pins that control the relays.
# When the ESP32 sets a pin HIGH (3.3 volts), the relay clicks ON.
# When it sets the pin LOW (0 volts), the relay clicks OFF.
#
# Note: Many relay modules are "active LOW" — meaning they turn ON when the pin
# is LOW and OFF when HIGH. We'll handle this in relay_control.py.
RELAY_1_PIN = 25  # Essential loads (lights, router) — never cut
RELAY_2_PIN = 26  # Secondary loads (fans, TV)
RELAY_3_PIN = 27  # Heavy loads (air conditioner)
RELAY_4_PIN = 14  # Extra heavy loads (water heater)

# Whether the relay module is active LOW (most cheap modules are).
# Active LOW = relay turns ON when GPIO is LOW (0V), OFF when HIGH (3.3V).
# This is confusing but common — many relay boards work this way.
RELAY_ACTIVE_LOW = True

# --- Reading & Timing Settings ---
# How often (in milliseconds) the ESP32 reads its sensors and sends data.
# 3000 ms = 3 seconds. This means we send a reading every 3 seconds.
# Faster = more real-time data but more Wi-Fi traffic and server load.
# Slower = less traffic but delays in detecting low battery.
TELEMETRY_INTERVAL_MS = 3000

# How many times to retry sending data if Wi-Fi or server is down before
# switching to "local fallback" mode (keeping last known relay states).
MAX_RETRIES = 3

# --- Sensor Calibration Values ---
# These numbers convert the raw ADC reading (0-4095) into real-world values.
# ADC on ESP32 reads 0 when the pin sees 0 volts, and 4095 when it sees 3.3 volts.
# We need math to turn those raw numbers into actual voltage/current.
# These values will need calibration with real sensors — explained in sensors.py.

# Voltage divider ratio: if your divider reduces voltage by 1/11 (common),
# then real_voltage = adc_voltage * 11.
VOLTAGE_DIVIDER_RATIO = 11.0

# For CT clamp: how many volts per amp the sensor outputs.
# SCT-013-30A sensor with a burden resistor typically outputs ~1V at 30A.
# This value converts the sensor output to actual amps.
CT_CALIBRATION_FACTOR = 30.0  # Max current the CT clamp can measure (30A)

# Reference voltage for ADC calculations
ADC_REFERENCE_VOLTAGE = 3.3
ADC_MAX_VALUE = 4095  # ESP32 ADC is 12-bit: 2^12 - 1 = 4095

# --- Battery State of Charge (SoC) Settings ---
# SoC = how full the battery is, as a percentage (like your phone battery %).
# We calculate this from voltage. For a 12V lead-acid battery:
#   ~12.6V = 100%   ~12.2V = 75%   ~11.8V = 50%   ~11.4V = 25%   ~10.5V = 0%
# These values map battery voltage to a percentage.
# (This is a simplified mapping — real batteries are non-linear.)
BATTERY_FULL_VOLTAGE = 12.6
BATTERY_EMPTY_VOLTAGE = 10.5

# --- Default Relay States (for local fallback) ---
# If the cloud is unreachable, the ESP32 uses these states.
# By default, all relays are ON (everything allowed).
DEFAULT_RELAY_STATES = [True, True, True, True]
