# AetherVane DSL App — The Dynamic Shedding Logic Engine
# =========================================================
# This is the BRAIN of the AetherVane system. It decides which relays
# should be ON or OFF based on the battery's current charge level.
#
# HOW IT WORKS (plain language):
#
# Picture a water tank (the battery) supplying a building with faucets (the appliances).
#
#   Tank full (100%)    -> all faucets open (normal)
#   Tank half (50%)     -> still fine, all open
#   Tank low (40%)     -> close the biggest faucet (water heater)
#   Tank very low (25%) -> also close the second biggest (air conditioner)
#   Tank almost empty (15%) -> close everything except the essentials (lights)
#
# When the tank refills (battery charges), we don't immediately open all faucets.
# We wait until the tank is meaningfully fuller (+10%) before re-opening a faucet.
# This prevents the faucets from rapidly opening and closing if the water level
# is hovering right at the cutoff point.
#
# THE ALGORITHM STEP BY STEP:
# 1. Receive the current battery SoC (percentage)
# 2. Determine the current "stage" based on thresholds
# 3. Check if we should CHANGE the stage (shed more or recover)
# 4. If shedding: cut relays according to the stage
# 5. If recovering: check hysteresis — only re-engage if SoC has recovered enough
# 6. Update relay_states in the database
# 7. Log any changes to alert_logs
# 8. Return the new relay states

from django.utils import timezone
from telemetry.models import RelayState, AlertLog
from .thresholds import (
    NORMAL_THRESHOLD, STAGE_1_THRESHOLD, STAGE_2_THRESHOLD,
    EMERGENCY_THRESHOLD, HYSTERESIS_RECOVERY,
    STAGE_RELAY_MAP, RECOVERY_THRESHOLDS
)


class DSLEngine:
    """
    The Dynamic Shedding Logic engine.
    
    Created fresh each time a telemetry packet arrives. It evaluates the
    current battery SoC, decides what the relay states should be, updates
    the database, and returns the result.
    """

    def __init__(self):
        # Track the previous stage for hysteresis logic
        self.previous_stage = None

    def _determine_stage(self, soc):
        """
        Determine the shedding stage based on battery SoC.
        
        Parameters:
          soc: Battery State of Charge as a percentage (0-100)
        
        Returns:
          A string: 'normal', 'stage_1', 'stage_2', or 'emergency'
        
        Stage mapping:
          SoC >= 50%  -> normal    (all 4 relays ON)
          40% <= SoC < 50% -> stage_1  (cut Relay 4)
          25% <= SoC < 40% -> stage_2  (cut Relay 3 + 4)
          SoC < 15%  -> emergency (cut Relay 2 + 3 + 4, only R1 stays)
        """
        if soc >= NORMAL_THRESHOLD:
            return 'normal'
        elif soc >= STAGE_1_THRESHOLD:
            return 'stage_1'
        elif soc >= STAGE_2_THRESHOLD:
            return 'stage_2'
        else:
            return 'emergency'

    def _should_recover(self, current_stage, previous_stage, soc):
        """
        Check if the battery has recovered enough to move to a less aggressive stage.
        
        HYSTERESIS LOGIC:
        If we were in stage_1 (cut at 40%) and the battery is now charging,
        we don't re-engage Relay 4 until SoC reaches 50% (40% + 10% hysteresis).
        
        This prevents "chattering" — the relay rapidly clicking on/off when
        the voltage hovers right at the threshold boundary.
        
        Parameters:
          current_stage: The stage the SoC would put us in right now
          previous_stage: The stage we were in last time (from DB)
          soc: Current battery SoC
        
        Returns:
          True if we should allow recovery (move to less aggressive stage),
          False if we should stay in the current (more aggressive) stage.
        """
        # If we're already at normal or the stage hasn't changed, no hysteresis needed
        if previous_stage is None:
            return True
        
        # Order of stages from most to least aggressive
        stage_order = ['emergency', 'stage_2', 'stage_1', 'normal']
        prev_idx = stage_order.index(previous_stage)
        current_idx = stage_order.index(current_stage)
        
        # If the new stage is less aggressive (higher index = fewer relays cut),
        # check hysteresis before allowing the recovery
        if current_idx > prev_idx:
            # The battery is recovering. Check if SoC has recovered enough.
            recovery_threshold = RECOVERY_THRESHOLDS.get(previous_stage, 0)
            if soc >= recovery_threshold:
                return True
            else:
                # Not enough recovery yet — stay in the more aggressive stage
                return False
        
        return True

    def evaluate(self, device, soc):
        """
        Main entry point: evaluate battery SoC and determine relay states.
        
        Parameters:
          device: The Device object (from sites.models)
          soc: Current battery State of Charge (float, 0-100)
        
        Returns:
          A dictionary with:
            'relay_states': [bool, bool, bool, bool] — the 4 relay ON/OFF states
            'action_taken': 'none', 'shed', or 'recover'
            'stage': 'normal', 'stage_1', 'stage_2', or 'emergency'
            'alerts': list of alert descriptions
        """
        # --- Get or create the relay state for this device ---
        relay_state, created = RelayState.objects.get_or_create(device=device)
        
        # Read the previous stage from the relay state's last_source
        # We store the stage name in a simple way: check which relays are ON
        previous_stage = self._infer_stage_from_relays(relay_state.as_list())
        
        # --- Determine the target stage based on current SoC ---
        target_stage = self._determine_stage(soc)
        
        # --- Check hysteresis: can we move to the target stage? ---
        # If target is less aggressive (recovery), check hysteresis
        can_recover = self._should_recover(target_stage, previous_stage, soc)
        
        if not can_recover:
            # Stay in the previous (more aggressive) stage
            actual_stage = previous_stage
            action_taken = 'none'
        elif target_stage != previous_stage:
            # Stage is changing
            stage_order = ['emergency', 'stage_2', 'stage_1', 'normal']
            prev_idx = stage_order.index(previous_stage) if previous_stage else 3
            target_idx = stage_order.index(target_stage)
            
            if target_idx > prev_idx:
                # Moving to a less aggressive stage = recovery
                actual_stage = target_stage
                action_taken = 'recover'
            else:
                # Moving to a more aggressive stage = shedding
                actual_stage = target_stage
                action_taken = 'shed'
        else:
            # Same stage as before
            actual_stage = target_stage
            action_taken = 'none'
        
        # --- Get the relay states for this stage ---
        new_relay_states = STAGE_RELAY_MAP.get(actual_stage, STAGE_RELAY_MAP['normal'])
        
        # --- Update the database if relay states changed ---
        alerts = []
        if new_relay_states != relay_state.as_list():
            source = 'dsl'
            relay_state.update_from_list(new_relay_states, source=source)
            
            # --- Log the event ---
            if action_taken == 'shed':
                alert = AlertLog.objects.create(
                    device=device,
                    event_type='shedding',
                    severity='warning' if actual_stage != 'emergency' else 'critical',
                    description="DSL {}: cut to {} (SoC: {}%)".format(
                        actual_stage, new_relay_states, round(soc, 1)
                    ),
                    battery_pct_at_event=soc,
                )
                alerts.append(str(alert))
            elif action_taken == 'recover':
                alert = AlertLog.objects.create(
                    device=device,
                    event_type='recovery',
                    severity='info',
                    description="DSL {}: recovered to {} (SoC: {}%)".format(
                        actual_stage, new_relay_states, round(soc, 1)
                    ),
                    battery_pct_at_event=soc,
                )
                alerts.append(str(alert))
        else:
            # No change — just update the source if it was manual and DSL is now taking over
            if relay_state.last_source == 'manual':
                # Don't override manual control unless DSL is shedding (more aggressive)
                if action_taken == 'shed':
                    relay_state.update_from_list(new_relay_states, source='dsl')
                    alert = AlertLog.objects.create(
                        device=device,
                        event_type='shedding',
                        severity='warning' if actual_stage != 'emergency' else 'critical',
                        description="DSL override: battery low ({}%), overriding manual control".format(round(soc, 1)),
                        battery_pct_at_event=soc,
                    )
                    alerts.append(str(alert))
                else:
                    # Keep manual states — return them as-is
                    new_relay_states = relay_state.as_list()
        
        return {
            'relay_states': new_relay_states,
            'action_taken': action_taken,
            'stage': actual_stage,
            'alerts': alerts,
        }

    def _infer_stage_from_relays(self, relay_states):
        """
        Determine which stage the current relay states correspond to.
        
        This is used to figure out the "previous stage" when the engine starts.
        By looking at which relays are ON, we can infer which stage was active.
        """
        for stage_name, stage_relays in STAGE_RELAY_MAP.items():
            if relay_states == stage_relays:
                return stage_name
        # If no exact match, assume normal
        return 'normal'
