# AetherVane Vane Node — Sensor Reading Module
# ===============================================
# This file handles reading the physical sensors connected to the ESP32.
# 
# WHAT THIS MODULE DOES (in plain language):
# The ESP32 has special pins that can "feel" electrical voltage — like
# how your skin can feel hot and cold. These pins read the raw electrical
# signals from the CT clamp (current sensor) and the voltage divider.
# Then we convert those raw numbers into meaningful values like
# "the battery is at 12.3 volts" or "the current is 2.5 amps."

import machine  # Built-in MicroPython module for hardware control (pins, ADC, etc.)
import math     # For square root calculation in RMS
import time     # For delays during sampling
from config import (
    VOLTAGE_SENSOR_PIN,
    CURRENT_SENSOR_PIN,
    VOLTAGE_DIVIDER_RATIO,
    CT_CALIBRATION_FACTOR,
    ADC_REFERENCE_VOLTAGE,
    ADC_MAX_VALUE,
    BATTERY_FULL_VOLTAGE,
    BATTERY_EMPTY_VOLTAGE,
)


class SensorReader:
    """
    Reads voltage and current sensors, and calculates battery State of Charge.
    
    ANALOGY: Think of this class as a "translator" standing between the raw
    electrical world (where everything is just a number 0-4095) and the human
    world (where we want to see "12.3 volts" and "2.5 amps").
    """

    def __init__(self):
        # --- Initialize the ADC (Analog-to-Digital Converter) pins ---
        # ADC = "Analog-to-Digital Converter"
        # "Analog" = a continuous signal (like a dimmer switch, can be any value)
        # "Digital" = only 0 or 1 (like a regular on/off switch)
        # The ADC converts the analog voltage on a pin into a digital number.
        # ESP32 ADC gives us a number from 0 to 4095:
        #   0 = 0 volts on the pin
        #   4095 = 3.3 volts on the pin
        #
        # We set attenuation to 11dB to allow reading up to ~3.3V (default is only 1.1V).
        # Attenuation = reducing the signal strength, like turning down volume.
        # 11dB attenuation lets the ADC read the full 0-3.3V range.
        
        self.voltage_adc = machine.ADC(machine.Pin(VOLTAGE_SENSOR_PIN))
        self.voltage_adc.atten(machine.ADC.ATTN_11DB)  # Allow 0-3.3V range
        
        self.current_adc = machine.ADC(machine.Pin(CURRENT_SENSOR_PIN))
        self.current_adc.atten(machine.ADC.ATTN_11DB)  # Allow 0-3.3V range

    def _read_adc_average(self, adc, num_samples=10):
        """
        Read the ADC pin multiple times and average the results.
        
        WHY AVERAGE? Because electrical signals have "noise" — tiny random
        fluctuations, like static on a radio. If you read just once, you might
        catch a spike. Reading 10 times and averaging gives a steadier number.
        
        ANALOGY: If you want to know someone's height, measuring once might be
        slightly off. Measuring 10 times and averaging gives you confidence.
        """
        total = 0
        for _ in range(num_samples):
            total += adc.read()
            time.sleep_ms(1)  # Tiny delay between readings (1 millisecond)
        return total / num_samples

    def read_voltage(self):
        """
        Read the battery voltage through the voltage divider circuit.
        
        WHAT HAPPENS STEP BY STEP:
        1. The battery's real voltage (e.g., 12.6V) goes through the voltage divider.
        2. The divider reduces it by a ratio (e.g., 11:1), so 12.6V becomes ~1.15V.
        3. The ADC pin reads that 1.15V and converts it to a number (0-4095).
        4. We convert that number back to the real voltage using math.
        
        The math: 
          adc_voltage = (raw_reading / 4095) * 3.3
          real_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO
        """
        raw = self._read_adc_average(self.voltage_adc)
        
        # Convert raw ADC number (0-4095) to voltage at the pin (0-3.3V)
        pin_voltage = (raw / ADC_MAX_VALUE) * ADC_REFERENCE_VOLTAGE
        
        # Multiply by the divider ratio to get the real battery voltage
        battery_voltage = pin_voltage * VOLTAGE_DIVIDER_RATIO
        
        # Round to 2 decimal places (e.g., 12.34 instead of 12.33928...)
        return round(battery_voltage, 2)

    def read_current(self):
        """
        Read the current flowing through the wire using the CT clamp.
        
        A CT (Current Transformer) clamp works by electromagnetic induction:
        When AC current flows through a wire, it creates a magnetic field
        around the wire. The CT clamp senses that magnetic field and converts
        it back into a small electrical signal proportional to the current.
        
        For the SCT-013 sensor, the output is a small AC voltage.
        We read the peak and convert to RMS (Root Mean Square).
        
        WHAT IS RMS? 
        AC current goes up and down like a wave (sine wave).
        The "peak" is the top of the wave, but the useful value is the RMS —
        which is like the "average effective" value. 
        For a sine wave: RMS = peak / 1.414 (which is square root of 2)
        
        ANALOGY: Think of ocean waves. The peak is the top of the wave,
        but if you want to know how much energy the waves carry on average,
        you use RMS — it's lower than the peak but represents real power.
        """
        # Read multiple samples to capture the AC waveform
        # For AC, we need to sample fast and find the peak
        samples = []
        for _ in range(50):
            samples.append(self.current_adc.read())
            time.sleep_ms(2)  # 2ms between samples
        
        # Find the peak value (highest reading)
        # The AC signal swings above and below a midpoint.
        # We find the maximum deviation from the midpoint.
        midpoint = ADC_MAX_VALUE / 2  # AC signals are centered at half the ADC range
        max_deviation = 0
        for s in samples:
            deviation = abs(s - midpoint)
            if deviation > max_deviation:
                max_deviation = deviation
        
        # Convert the peak ADC deviation to peak voltage at the pin
        peak_pin_voltage = (max_deviation / ADC_MAX_VALUE) * ADC_REFERENCE_VOLTAGE
        
        # Convert peak to RMS (divide by square root of 2)
        rms_pin_voltage = peak_pin_voltage / math.sqrt(2)
        
        # Convert the sensor output voltage to actual current (amps)
        # The calibration factor maps sensor voltage to real current
        current_amps = (rms_pin_voltage * CT_CALIBRATION_FACTOR) / 3.3
        
        # For a prototype without real CT clamp connected, return 0
        # (so the system doesn't crash when no sensor is attached)
        if current_amps < 0:
            current_amps = 0
        
        return round(current_amps, 2)

    def calculate_wattage(self, voltage, current):
        """
        Calculate power (watts) from voltage and current.
        
        This is basic physics: Power = Voltage x Current
        Like how water pressure x water flow = how much energy the water carries.
        
        Example: 12V x 2.5A = 30W (like a small light bulb)
        """
        if voltage < 0 or current < 0:
            return 0
        watts = voltage * current
        return round(watts, 2)

    def calculate_battery_soc(self, voltage):
        """
        Estimate the battery State of Charge (SoC) as a percentage.
        
        SoC = "State of Charge" = how full the battery is, from 0% to 100%.
        Like the battery percentage on your phone.
        
        We estimate SoC from voltage because lower voltage = lower charge.
        For a 12V lead-acid battery:
          12.6V = 100% (full)
          10.5V = 0% (empty / dangerously low)
        
        We do a simple linear mapping between these two points.
        (Real battery SoC curves are non-linear, but linear is fine for a prototype.)
        
        MATH:
          If voltage is 12.6V -> 100%
          If voltage is 10.5V -> 0%
          Formula: percentage = ((voltage - 10.5) / (12.6 - 10.5)) * 100
        """
        if voltage >= BATTERY_FULL_VOLTAGE:
            return 100.0
        elif voltage <= BATTERY_EMPTY_VOLTAGE:
            return 0.0
        else:
            soc = ((voltage - BATTERY_EMPTY_VOLTAGE) / 
                   (BATTERY_FULL_VOLTAGE - BATTERY_EMPTY_VOLTAGE)) * 100
            return round(soc, 1)

    def read_all(self):
        """
        Convenience method: read all sensors and return a complete data packet.
        
        Returns a dictionary (like a labeled box) with all the readings:
        {
            "voltage": 12.3,
            "current": 2.5,
            "wattage": 30.75,
            "battery_pct": 85.7
        }
        """
        voltage = self.read_voltage()
        current = self.read_current()
        wattage = self.calculate_wattage(voltage, current)
        battery_pct = self.calculate_battery_soc(voltage)
        
        return {
            "voltage": voltage,
            "current": current,
            "wattage": wattage,
            "battery_pct": battery_pct
        }
