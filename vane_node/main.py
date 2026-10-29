# AetherVane Vane Node — Main Entry Point
# ========================================
# This is the "conductor" of the Vane Node — it starts everything up and
# runs the main loop that keeps the system alive.
#
# WHAT THIS FILE DOES (in plain language):
# Think of main.py as the manager of a factory. The manager:
#   1. Opens the factory (boots up the ESP32)
#   2. Makes sure all workers are ready (Wi-Fi, sensors, relays)
#   3. Runs the main work loop:
#      a. Read the sensors (check the battery's health)
#      b. Send the readings to the cloud (report to headquarters)
#      c. Get back relay commands (receive instructions)
#      d. Apply the relay commands (flip the switches)
#      e. Wait a few seconds, then repeat
#
# LOCAL FALLBACK:
# If the cloud is unreachable (Wi-Fi down or server down), the manager
# keeps using the last known relay states. The system doesn't stop —
# it just keeps running on its own until the cloud comes back.
# This is critical: if the cloud goes down, you don't want the battery
# to be left unprotected.

import time
from config import TELEMETRY_INTERVAL_MS, MAX_RETRIES
from sensors import SensorReader
from relay_control import RelayController
from network import NetworkManager


def main():
    """
    Main function — the entry point of the Vane Node.
    This runs when the ESP32 powers on.
    """
    print("=" * 50)
    print("  AetherVane Vane Node — Starting Up")
    print("=" * 50)
    
    # --- Step 1: Initialize all subsystems ---
    # Each line below creates an object (a working instance) of a module.
    # Think of this as hiring workers and getting them to their stations.
    
    print("\n[1/4] Initializing sensors...")
    sensors = SensorReader()
    print("      Sensors ready: voltage divider + CT clamp")
    
    print("\n[2/4] Initializing relay controller...")
    relays = RelayController()
    print("      Relays ready: 4 channels initialized")
    print("      " + relays.get_status_text())
    
    print("\n[3/4] Initializing network manager...")
    net = NetworkManager()
    
    # Connect to Wi-Fi
    print("\n[4/4] Connecting to Wi-Fi...")
    wifi_ok = net.connect_wifi()
    
    if wifi_ok:
        print("\n      Wi-Fi connected! Ready to communicate with cloud.")
    else:
        print("\n      WARNING: Wi-Fi not connected!")
        print("      Starting in LOCAL FALLBACK mode.")
        print("      Will retry Wi-Fi connection in main loop.")
    
    # Get the ESP32's MAC address (unique hardware ID)
    mac_address = net.get_mac_address()
    print("\n[Vane Node] MAC Address: {}".format(mac_address))
    
    # Track consecutive failures for fallback logic
    consecutive_failures = 0
    
    print("\n" + "=" * 50)
    print("  Vane Node operational. Entering main loop.")
    print("  Telemetry interval: {}ms".format(TELEMETRY_INTERVAL_MS))
    print("=" * 50 + "\n")
    
    # --- Step 2: Main Loop ---
    # This loop runs forever (until the ESP32 is powered off or reset).
    # Each iteration:
    #   1. Read sensors
    #   2. Send telemetry to cloud
    #   3. Apply returned relay states (or use fallback)
    #   4. Wait, then repeat
    
    while True:
        try:
            # --- 2a: Read sensors ---
            # Get current voltage, current, wattage, and battery percentage
            sensor_data = sensors.read_all()
            
            # Include current relay states in the telemetry so the server knows
            # what the relays are currently doing
            sensor_data["relay_states"] = relays.get_states()
            
            print("\n--- Telemetry Cycle ---")
            print("[Sensors] Voltage: {}V | Current: {}A | Power: {}W | Battery: {}%".format(
                sensor_data["voltage"],
                sensor_data["current"],
                sensor_data["wattage"],
                sensor_data["battery_pct"]
            ))
            
            # --- 2b: Send telemetry to cloud ---
            # The server processes the data and returns updated relay states
            cloud_relay_states = net.send_telemetry(sensor_data, mac_address)
            
            # --- 2c: Apply relay states ---
            if cloud_relay_states is not None:
                # Cloud responded with relay states — apply them
                print("[Cloud] Received relay states: {}".format(cloud_relay_states))
                relays.apply_cloud_states(cloud_relay_states)
                consecutive_failures = 0
                print("[Relays] " + relays.get_status_text())
            else:
                # Cloud didn't respond — use local fallback
                consecutive_failures += 1
                print("[Fallback] Cloud unreachable (failure #{}/{}).".format(
                    consecutive_failures, MAX_RETRIES))
                print("[Fallback] Keeping last known relay states.")
                print("[Relays] " + relays.get_status_text())
                
                # If we've failed many times, try to reconnect Wi-Fi
                if consecutive_failures >= MAX_RETRIES:
                    print("[Fallback] Attempting Wi-Fi reconnect...")
                    net.connect_wifi()
                    consecutive_failures = 0  # Reset after reconnect attempt
            
            # --- 2d: Wait before next cycle ---
            # Sleep for the configured interval before reading sensors again
            time.sleep_ms(TELEMETRY_INTERVAL_MS)
            
        except Exception as e:
            # If anything crashes in the loop, catch the error and keep running.
            # We don't want the Vane Node to stop working because of a bug.
            # This is like a factory manager catching a problem and keeping
            # the line running instead of shutting everything down.
            print("[ERROR] Main loop exception: {}".format(str(e)))
            print("[ERROR] Continuing in 3 seconds...")
            time.sleep_ms(3000)


# This is the standard MicroPython entry point.
# When the ESP32 boots, MicroPython automatically runs main.py.
# The if __name__ check ensures this code only runs when the file is
# executed directly (not when imported by another file).
if __name__ == "__main__":
    main()
