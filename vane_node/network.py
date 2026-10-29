# AetherVane Vane Node — Network Communication Module
# =====================================================
# This file handles all Wi-Fi and internet communication for the Vane Node.
#
# WHAT THIS MODULE DOES (in plain language):
# The ESP32 needs to talk to the cloud server (our Django backend) to:
#   1. Send sensor readings (voltage, current, wattage, battery %)
#   2. Receive relay commands (which switches should be ON or OFF)
#
# It does this over Wi-Fi, using HTTP — the same protocol your web browser
# uses to load websites. Specifically, it sends "POST" requests (like submitting
# a form on a website) with the sensor data packaged as JSON.
#
# WHAT IS JSON?
# JSON (JavaScript Object Notation) is just a way to format data as text.
# It looks like this:
#   {"voltage": 12.3, "current": 2.5, "wattage": 30.75, "battery_pct": 85.7}
# Think of it as a labeled box: each label (like "voltage") has a value (like 12.3).
# The cloud server reads these labels to get the sensor data.
#
# WHAT IS HTTP POST?
# HTTP is the language of the web. There are different "verbs" (actions):
#   GET  = "give me information" (like opening a webpage)
#   POST = "here is information" (like submitting a form)
# We use POST because we're SENDING data to the server.

import network   # MicroPython built-in module for Wi-Fi
import urequests # MicroPython built-in module for HTTP requests (like a mini browser)
import ujson     # MicroPython built-in module for JSON (packaging data as text)
import time
from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    SERVER_URL,
    TELEMETRY_ENDPOINT,
    RELAY_COMMAND_ENDPOINT,
    DEVICE_TOKEN,
    MAX_RETRIES,
)


class NetworkManager:
    """
    Manages Wi-Fi connection and all HTTP communication with the cloud server.
    
    ANALOGY: Think of this class as a "mailroom" for the Vane Node.
    - connect_wifi() = setting up the mail delivery route (connecting to the internet)
    - send_telemetry() = mailing a letter with sensor readings to the cloud
    - fetch_relay_states() = checking the mailbox for new relay commands
    """

    def __init__(self):
        # Create a Wi-Fi station interface (the ESP32 in "client" mode, connecting
        # to an existing Wi-Fi network, like your phone connecting to Wi-Fi)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.connected = False
        self.retry_count = 0

    def connect_wifi(self, timeout_ms=15000):
        """
        Connect to the Wi-Fi network specified in config.py.
        
        Parameters:
          timeout_ms: How long to wait before giving up (15 seconds default)
        
        Returns:
          True if connected successfully, False if it failed
        
        WHAT HAPPENS:
        1. The ESP32 scans for the Wi-Fi network named in WIFI_SSID
        2. It tries to connect using the password in WIFI_PASSWORD
        3. It waits until connected or timeout
        4. Once connected, it gets an IP address (like a phone number for the network)
        """
        if self.wlan.isconnected():
            print("[Network] Already connected to Wi-Fi")
            self.connected = True
            return True
        
        print("[Network] Connecting to Wi-Fi: {}...".format(WIFI_SSID))
        self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection, checking every 500ms
        start_time = time.ticks_ms()
        while not self.wlan.isconnected():
            elapsed = time.ticks_diff(time.ticks_ms(), start_time)
            if elapsed > timeout_ms:
                print("[Network] Wi-Fi connection timed out after {}ms".format(timeout_ms))
                self.connected = False
                return False
            time.sleep_ms(500)
            print(".", end="")
        
        # Connected! Print the IP address assigned to the ESP32
        ip_info = self.wlan.ifconfig()
        # ifconfig() returns (ip, subnet, gateway, DNS)
        print("\n[Network] Connected! IP address: {}".format(ip_info[0]))
        self.connected = True
        self.retry_count = 0
        return True
    
    def is_connected(self):
        """
        Check if Wi-Fi is currently connected.
        Returns True or False.
        """
        return self.wlan.isconnected()
    
    def _build_headers(self):
        """
        Build HTTP headers for the request.
        
        HTTP headers are like the envelope of a letter — they tell the server
        what kind of content is inside and who is sending it.
        
        We include:
        - Content-Type: application/json (the data inside is JSON format)
        - Authorization: Token <device_token> (like showing an ID card)
        """
        return {
            "Content-Type": "application/json",
            "Authorization": "Token {}".format(DEVICE_TOKEN)
        }
    
    def send_telemetry(self, sensor_data, mac_address):
        """
        Send sensor readings to the cloud server.
        
        Parameters:
          sensor_data: Dictionary with voltage, current, wattage, battery_pct
          mac_address: The ESP32's MAC address (unique hardware ID)
        
        Returns:
          A list of relay states if successful, or None if failed.
          Example: [True, True, False, False]
        
        WHAT HAPPENS STEP BY STEP:
        1. Package the sensor data + MAC address into a JSON string
        2. Send an HTTP POST request to the server
        3. The server processes the data, runs the DSL engine,
           and returns updated relay states
        4. We return those relay states so main.py can apply them to the physical relays
        
        LOCAL FALLBACK:
        If the server is unreachable (Wi-Fi down, server down), we increment
        retry_count. After MAX_RETRIES failures, we return None, which tells
        main.py to use the last known relay states (local fallback mode).
        """
        if not self.is_connected():
            print("[Network] Wi-Fi not connected. Attempting reconnect...")
            if not self.connect_wifi():
                self.retry_count += 1
                if self.retry_count >= MAX_RETRIES:
                    print("[Network] Max retries reached. Entering local fallback mode.")
                return None
        
        # Build the JSON payload (the "letter" we're sending)
        payload = {
            "mac_address": mac_address,
            "voltage": sensor_data["voltage"],
            "current": sensor_data["current"],
            "wattage": sensor_data["wattage"],
            "battery_pct": sensor_data["battery_pct"],
            "relay_states": sensor_data.get("relay_states", [True, True, True, True])
        }
        
        url = SERVER_URL + TELEMETRY_ENDPOINT
        json_str = ujson.dumps(payload)
        
        print("[Network] Sending telemetry to {}...".format(url))
        print("[Network] Payload: {}".format(json_str))
        
        try:
            response = urequests.post(
                url,
                data=json_str,
                headers=self._build_headers()
            )
            
            # Check if the server accepted our data (HTTP 200 = OK)
            if response.status_code == 200:
                print("[Network] Telemetry sent successfully!")
                self.retry_count = 0
                
                # Parse the server's response to get updated relay states
                response_data = ujson.loads(response.text)
                relay_states = response_data.get("relay_states", None)
                
                response.close()
                return relay_states
            else:
                print("[Network] Server returned error: HTTP {}".format(response.status_code))
                response.close()
                self.retry_count += 1
                return None
                
        except Exception as e:
            # Network errors (timeout, DNS failure, server unreachable) land here
            print("[Network] Error sending telemetry: {}".format(str(e)))
            self.retry_count += 1
            return None
    
    def fetch_relay_states(self, mac_address):
        """
        Fetch the latest relay states from the cloud server.
        
        This is used when we want to check if there are manual overrides
        (a user clicked a relay toggle in the web dashboard).
        
        Parameters:
          mac_address: The ESP32's MAC address
        
        Returns:
          A list of 4 True/False values, or None if fetch failed.
        """
        if not self.is_connected():
            return None
        
        url = SERVER_URL + RELAY_COMMAND_ENDPOINT + "?mac=" + mac_address
        
        try:
            response = urequests.get(url, headers=self._build_headers())
            
            if response.status_code == 200:
                data = ujson.loads(response.text)
                response.close()
                return data.get("relay_states", None)
            else:
                response.close()
                return None
                
        except Exception as e:
            print("[Network] Error fetching relay states: {}".format(str(e)))
            return None
    
    def get_mac_address(self):
        """
        Get the ESP32's unique MAC address.
        
        The MAC address is a hardware-level unique identifier — every ESP32
        has a different one, assigned at the factory. It looks like:
        "AA:BB:CC:DD:EE:FF"
        
        We send this to the server so it knows WHICH device is talking.
        It's like the device showing its ID card.
        """
        mac_bytes = self.wlan.config("mac")
        # mac_bytes is a bytes object like b'\xaa\xbb\xcc\xdd\xee\xff'
        # Convert it to a readable string format: "AA:BB:CC:DD:EE:FF"
        mac_str = ":".join("{:02X}".format(b) for b in mac_bytes)
        return mac_str
