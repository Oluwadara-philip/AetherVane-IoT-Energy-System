# Project AetherVane

**IoT-Enabled Multi-Tenant Energy Monitoring and Automated Load-Shedding System**

An IoT platform that protects battery banks in solar/inverter setups from deep discharge damage by automatically cutting off heavy appliances when battery voltage drops below safe thresholds.

## Architecture Overview

```
[Vane Node]  --HTTPS POST-->  [Aether Core Engine]  --ORM-->  [MySQL]
   (ESP32)                     (Django REST API)               (aethervane_db)
                                   ^
                                   |
                              [Vane Central]
                              (Vue.js Dashboard)
```

## Project Structure

```
AetherVane/
  vane_node/          — ESP32 MicroPython firmware (edge device)
  aether_core/        — Django REST backend (cloud API + DSL engine)
  vane_central/       — Vue.js frontend (web dashboard)
```

## Quick Start

### 1. Backend (Django)
```bash
cd aether_core
pip install -r requirements.txt
cp .env.example .env  # Edit with your MySQL credentials
python manage.py makemigrations accounts sites telemetry
python manage.py migrate
python manage.py createsuperuser  # Create your admin account
python manage.py runserver 0.0.0.0:8000
```

### 2. Frontend (Vue.js)
```bash
cd vane_central
npm install
npm run dev  # Opens on http://localhost:5173
```

### 3. Vane Node (ESP32)
1. Flash MicroPython onto ESP32 using Thonny IDE
2. Edit `vane_node/config.py` with your Wi-Fi and server settings
3. Upload all .py files to the ESP32 via Thonny
4. Register the device in Django admin to get the API token
5. Put the token in config.py and reboot the ESP32

## Key Concepts

- **Vane Node**: ESP32 with CT clamps, voltage divider, 4-channel relay
- **Aether Core Engine**: Django REST API with JWT auth, multi-tenant RBAC
- **Dynamic Shedding Logic (DSL)**: Auto-cuts relays in priority tiers when battery SoC drops
- **Vane Central**: Dark-mode glassmorphism dashboard with live gauges and relay controls

## Tech Stack
- ESP32 + MicroPython (edge)
- Django 4.2 + DRF + SimpleJWT + MySQL (backend)
- Vue.js 3 + Tailwind CSS + ECharts + Pinia (frontend)
