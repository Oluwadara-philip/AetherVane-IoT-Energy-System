# AetherVane DSL App — Threshold Configuration
# ===============================================
# This file holds the battery SoC (State of Charge) thresholds that trigger
# load shedding. Think of it as the "rules of the game" — at what battery
# level do we start cutting appliances?
#
# THE 4 SHEDDING STAGES (plain language):
#
# STAGE 0 (Normal): Battery is healthy (SoC >= 50%)
#   All 4 relays ON. Everything works normally.
#   Like a full gas tank — drive as much as you want.
#
# STAGE 1 (Warning): Battery getting low (25% <= SoC < 50%)
#   Cut Relay 4 (extra heavy: water heater, pumps)
#   Like seeing your gas gauge at 1/4 — start being conservative.
#
# STAGE 2 (Critical): Battery very low (15% <= SoC < 25%)
#   Cut Relay 3 + Relay 4 (heavy: AC, fridge + extra heavy)
#   Like gas gauge almost empty — turn off the AC, save fuel.
#
# STAGE 3 (Emergency): Battery dangerously low (SoC < 15%)
#   Cut Relay 2 + 3 + 4 (only essential loads remain: lights, router)
#   Like running on fumes — only keep the essentials alive.
#
# HYSTERESIS (+10% recovery):
#   Once a relay is cut, the battery must recover by +10% SoC before
#   that relay turns back on. This prevents "chattering" — the relay
#   rapidly clicking on/off when the voltage hovers near a threshold.
#
#   Example: Relay 4 is cut at SoC 40%. It won't turn back on until
#   SoC reaches 50% (40% + 10% hysteresis).
#
#   ANALOGY: Think of a thermostat. If you set it to 20°C and it turns
#   off at exactly 20.0°C, it would click on/off constantly as the
#   temperature hovers. Instead, thermostats wait until 21°C to turn off
#   and 19°C to turn on — a 2°C "gap" that prevents chattering.

# --- Threshold Values ---
# These are the SoC percentages at which each stage triggers.

# Below this: everything is normal (all relays ON)
NORMAL_THRESHOLD = 50.0

# Below this: Stage 1 (cut Relay 4)
STAGE_1_THRESHOLD = 40.0

# Below this: Stage 2 (cut Relay 3 + 4)
STAGE_2_THRESHOLD = 25.0

# Below this: Emergency (cut Relay 2 + 3 + 4)
EMERGENCY_THRESHOLD = 15.0

# Hysteresis: how much the battery must recover above a threshold
# before re-engaging a cut relay
HYSTERESIS_RECOVERY = 10.0

# Default relay states by stage (which relays are ON in each stage)
# [Relay 1, Relay 2, Relay 3, Relay 4]
STAGE_RELAY_MAP = {
    'normal':    [True, True, True, True],    # SoC >= 50%
    'stage_1':   [True, True, True, False],   # 40% <= SoC < 50%
    'stage_2':   [True, True, False, False],  # 25% <= SoC < 40%
    'emergency': [True, False, False, False], # SoC < 15%
}

# Threshold + hysteresis for re-engagement
# If a relay was cut at stage_1 (40%), it needs SoC >= 50% to re-engage
# 40 + 10 = 50 (which is the NORMAL_THRESHOLD)
RECOVERY_THRESHOLDS = {
    'stage_1': STAGE_1_THRESHOLD + HYSTERESIS_RECOVERY,   # 50%
    'stage_2': STAGE_2_THRESHOLD + HYSTERESIS_RECOVERY,   # 35%
    'emergency': EMERGENCY_THRESHOLD + HYSTERESIS_RECOVERY, # 25%
}
