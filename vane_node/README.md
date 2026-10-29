# AetherVane Vane Node — MicroPython Firmware

## What This Is
The "Vane Node" is the physical edge device of the AetherVane system. It's an ESP32 microcontroller that reads battery voltage and current, sends that data to the cloud over Wi-Fi, and controls 4 relays that can cut power to appliances when the battery is running low.

## Hardware Required (~120 RMB total on Taobao)
| Component | Est. Price | Purpose |
|-----------|-----------|---------|
| ESP32 Dev Board | ~30 RMB | The "brain" — runs MicroPython, has Wi-Fi |
| SCT-013-30A CT Clamp | ~20 RMB | Measures current (non-invasive, clips around wire) |
| 4-Channel Relay Module | ~15 RMB | Electronic switches for 4 appliance circuits |
| Resistors + Breadboard | ~10 RMB | Voltage divider circuit + prototyping |
| Jumper Wires | ~5 RMB | Connect everything together |
| USB Cable + Power Supply | ~10 RMB | Power the ESP32 |
| **Total** | **~90-120 RMB** | |

## File Structure
```
vane_node/
  config.py           — Settings (Wi-Fi, server URL, pin numbers, calibration)
  sensors.py          — Reads CT clamp + voltage divider, calculates wattage + SoC
  relay_control.py    — Controls the 4-channel relay module (ON/OFF per circuit)
  network.py          — Wi-Fi connection + HTTP POST telemetry + fetch relay commands
  main.py             — Entry point: boots up, runs main loop forever
```

## How to Flash MicroPython onto the ESP32
1. Download the Thonny IDE (free): https://thonny.org
2. Plug the ESP32 into your computer via USB
3. In Thonny: Tools > Options > Interpreter > select "ESP32"
4. Click "Install MicroPython" and follow the prompts
5. After flashing, open each .py file in Thonny and save it to the ESP32
   (File > Save As > MicroPython device)

## Before Running
Edit `config.py` and change:
- `WIFI_SSID` — your Wi-Fi network name
- `WIFI_PASSWORD` — your Wi-Fi password  
- `SERVER_URL` — your computer's IP address where Django will run (e.g., http://192.168.1.100:8000)
- `DEVICE_TOKEN` — you'll get this after registering the device in the Django backend

## How the Main Loop Works
```
  [Read Sensors] -> [Send to Cloud] -> [Get Relay Commands] -> [Apply to Relays]
        ^                                                                    |
        |____________________________________________________________________|
                              (repeat every 3 seconds)
```

If the cloud is unreachable, the Vane Node keeps using the last known relay states (local fallback) and keeps trying to reconnect.

## Safety Note
For development and testing, ONLY use low-voltage DC loads (LEDs, small fans, USB devices) connected to the relay module. NEVER connect mains AC (220V) during development. The relay module can handle AC, but testing should always be done at safe voltages.
