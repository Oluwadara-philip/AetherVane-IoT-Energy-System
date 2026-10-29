# AetherVane Vane Node — Relay Control Module
# ==============================================
# This file controls the 4 relay switches that turn appliance circuits on/off.
#
# WHAT IS A RELAY? (Plain language explanation)
# A relay is an electronic switch. A regular light switch needs your finger
# to flip it. A relay flips itself when it receives an electrical signal.
#
# Think of a relay like a remote-controlled light switch:
# - The ESP32 sends a small electrical signal (like pressing a button on a remote)
# - The relay "hears" that signal and clicks ON or OFF
# - The relay handles the big power going to the appliance
# - The ESP32 only handles tiny control signals (safe!)
#
# WHY NOT JUST CONNECT THE ESP32 DIRECTLY TO THE APPLIANCE?
# Because the ESP32 works at 3.3 volts and can only handle tiny currents.
# Appliances like air conditioners use 220V and many amps.
# The relay is the "middleman" — the ESP32 controls the relay,
# and the relay controls the big power. This keeps the ESP32 safe.
#
# ACTIVE LOW vs ACTIVE HIGH:
# Most cheap relay modules are "active LOW" — this means:
#   GPIO pin = LOW (0 volts) -> relay turns ON
#   GPIO pin = HIGH (3.3 volts) -> relay turns OFF
# This is the opposite of what you'd expect! It's a quirk of the hardware design.
# We handle this in the code so you don't have to think about it.

from machine import Pin
import time
from config import (
    RELAY_1_PIN,
    RELAY_2_PIN,
    RELAY_3_PIN,
    RELAY_4_PIN,
    RELAY_ACTIVE_LOW,
    DEFAULT_RELAY_STATES,
)


class RelayController:
    """
    Controls the 4-channel relay module.
    
    The relays are organized by priority:
      Relay 1: Essential loads (lights, router, security) -- NEVER cut automatically
      Relay 2: Secondary loads (fans, TV, office equipment)
      Relay 3: Heavy loads (air conditioner, fridge)
      Relay 4: Extra heavy loads (water heater, pumps)
    
    When battery gets low, we cut from the bottom (Relay 4 first, then 3, then 2).
    Relay 1 is always left on -- you don't want to lose lights and security.
    """

    def __init__(self):
        # --- Set up the GPIO pins for each relay ---
        # Pin.OUT means the pin is in "output" mode -- the ESP32 sends signals OUT.
        # (The alternative is Pin.IN, where the ESP32 listens for incoming signals.)
        
        self.relay_pins = [
            Pin(RELAY_1_PIN, Pin.OUT),  # Relay 1 - Essential
            Pin(RELAY_2_PIN, Pin.OUT),  # Relay 2 - Secondary
            Pin(RELAY_3_PIN, Pin.OUT),  # Relay 3 - Heavy
            Pin(RELAY_4_PIN, Pin.OUT),  # Relay 4 - Extra Heavy
        ]
        
        # Names for each relay (for logging and display)
        self.relay_names = [
            "Essential Loads",
            "Secondary Loads",
            "Heavy Loads",
            "Extra Heavy Loads"
        ]
        
        # --- Track relay states in memory ---
        # This list remembers the current state of each relay: [True, True, True, True]
        # True = relay is ON (power flowing), False = relay is OFF (power cut)
        # We keep this in memory so we can fall back to these if the cloud is unreachable.
        self.current_states = list(DEFAULT_RELAY_STATES)
        
        # Apply default states immediately on startup
        self.set_all_relays(self.current_states)
    
    def _get_pin_value(self, relay_on):
        """
        Convert a desired relay state (ON/OFF) to the GPIO value to write.
        
        If the relay module is "active LOW":
          Relay ON  -> GPIO LOW (0)
          Relay OFF -> GPIO HIGH (1)
        
        If the relay module is "active HIGH" (normal logic):
          Relay ON  -> GPIO HIGH (1)
          Relay OFF -> GPIO LOW (0)
        
        This method handles the conversion so the rest of the code
        can just think in terms of "ON" and "OFF" without worrying about
        the active LOW / HIGH confusion.
        """
        if RELAY_ACTIVE_LOW:
            # Active LOW: ON means LOW (0), OFF means HIGH (1)
            return 0 if relay_on else 1
        else:
            # Active HIGH: ON means HIGH (1), OFF means LOW (0)
            return 1 if relay_on else 0
    
    def set_relay(self, relay_index, state):
        """
        Turn a specific relay ON or OFF.
        
        Parameters:
          relay_index: 0-3 (0=Relay 1, 1=Relay 2, etc.)
          state: True (ON) or False (OFF)
        """
        if relay_index < 0 or relay_index > 3:
            return
        
        pin_value = self._get_pin_value(state)
        self.relay_pins[relay_index].value(pin_value)
        self.current_states[relay_index] = state
        
        # Print status (useful for debugging -- finding problems during development)
        status_text = "ON" if state else "OFF"
        print("[Relay {}] {}: {}".format(relay_index + 1, self.relay_names[relay_index], status_text))
    
    def set_all_relays(self, states):
        """
        Set all 4 relays at once.
        
        Parameters:
          states: A list of 4 True/False values, e.g. [True, True, False, False]
                  meaning Relay 1 ON, Relay 2 ON, Relay 3 OFF, Relay 4 OFF
        """
        for i in range(4):
            self.set_relay(i, states[i])
    
    def apply_cloud_states(self, relay_states):
        """
        Apply relay states received from the cloud server.
        
        The cloud sends a list like [true, true, false, false] meaning:
        Relay 1 = ON, Relay 2 = ON, Relay 3 = OFF, Relay 4 = OFF
        
        This method applies those states to the physical relays.
        It also updates our in-memory cache for fallback.
        """
        if len(relay_states) != 4:
            print("[Relay] Warning: Expected 4 relay states, got", len(relay_states))
            return
        
        self.set_all_relays(relay_states)
    
    def get_states(self):
        """
        Return the current relay states as a list of True/False values.
        
        Example return: [True, True, False, False]
        This means Relay 1 is ON, Relay 2 is ON, Relay 3 is OFF, Relay 4 is OFF.
        
        This is used for:
        1. Sending current states to the cloud in telemetry packets
        2. Logging what the relays are doing right now
        """
        return list(self.current_states)
    
    def get_status_text(self):
        """
        Return a human-readable summary of all relay states.
        Useful for printing to the serial console during development.
        """
        lines = []
        for i in range(4):
            status = "ON " if self.current_states[i] else "OFF"
            lines.append("R{}: {} ({})".format(i + 1, status, self.relay_names[i]))
        return " | ".join(lines)
