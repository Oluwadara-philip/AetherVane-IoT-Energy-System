# AetherVane Telemetry App — Views (API Endpoints)
# ==================================================
# These views handle:
#   1. INGESTION: Receiving sensor data from ESP32 devices
#   2. HISTORY: Serving telemetry data to the Vue.js dashboard
#   3. RELAY CONTROL: Manual relay overrides from the dashboard
#   4. ALERTS: Serving alert/event logs to the dashboard

from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from sites.models import Device
from .models import PowerReading, RelayState, AlertLog
from .serializers import (
    PowerReadingSerializer, RelayStateSerializer,
    AlertLogSerializer, TelemetryIngestSerializer
)
from accounts.permissions import IsSiteManagerOrAbove
from dsl.engine import DSLEngine


class TelemetryIngestView(APIView):
    """
    POST /api/v1/telemetry/ingest/
    
    This is THE most important endpoint in the whole system.
    The ESP32 sends sensor data here every 3 seconds.
    
    WHAT HAPPENS STEP BY STEP:
    1. Receive JSON payload from ESP32 (voltage, current, etc.)
    2. Look up the device by MAC address (verify it's registered)
    3. Store the reading in power_readings table
    4. Run the DSL engine to check if relay states need to change
    5. Update relay_states if DSL decided to cut/re-engage relays
    6. Return updated relay states to the ESP32
    
    AUTHENTICATION:
    The ESP32 sends its API token in the Authorization header.
    We verify the token matches the registered device.
    This prevents fake devices from injecting false data.
    """
    # AllowAny because ESP32 uses token auth, not JWT
    # (JWT is for web users; ESP32 uses a simpler device token)
    permission_classes = []
    
    def post(self, request):
        serializer = TelemetryIngestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        mac_address = data['mac_address']
        
        # --- Step 1: Find the device by MAC address ---
        try:
            device = Device.objects.get(mac_address=mac_address)
        except Device.DoesNotExist:
            return Response(
                {'error': 'Device not registered. MAC: {}'.format(mac_address)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # --- Step 2: Verify device authentication ---
        # Check the Authorization header matches the device's API token
        auth_header = request.headers.get('Authorization', '')
        token_part = auth_header.replace('Token ', '').strip()
        if token_part != device.api_token:
            return Response(
                {'error': 'Invalid device token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # --- Step 3: Store the telemetry reading ---
        reading = PowerReading.objects.create(
            device=device,
            voltage=data['voltage'],
            current=data['current'],
            wattage=data['wattage'],
            battery_pct=data['battery_pct'],
        )
        
        # Update device status and heartbeat
        device.device_status = 'online'
        device.last_heartbeat = timezone.now()
        device.save()
        
        # --- Step 4: Run the DSL Engine ---
        # The DSL engine checks battery_pct against thresholds and decides
        # which relays should be ON or OFF.
        dsl = DSLEngine()
        result = dsl.evaluate(device, data['battery_pct'])
        
        # result contains: {
        #   'relay_states': [True, True, False, False],
        #   'action_taken': 'shed' or 'recover' or 'none',
        #   'stage': 'normal' or 'stage_1' or 'stage_2' or 'emergency',
        #   'alerts': [...]
        # }
        
        # --- Step 5: Return updated relay states to ESP32 ---
        return Response({
            'status': 'ok',
            'reading_id': reading.id,
            'relay_states': result['relay_states'],
            'dsl_stage': result['stage'],
            'dsl_action': result['action_taken'],
        }, status=status.HTTP_200_OK)


class TelemetryHistoryView(APIView):
    """
    GET /api/v1/telemetry/history/?device_id=X&hours=24
    
    Returns historical sensor readings for charts.
    The Vue.js dashboard calls this to draw the voltage/current/wattage
    charts over the last 24 hours.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        device_id = request.query_params.get('device_id')
        hours = int(request.query_params.get('hours', 24))
        
        if not device_id:
            return Response({'error': 'device_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the user can access this device (multi-tenant check)
        try:
            if request.user.is_super_admin:
                device = Device.objects.get(id=device_id)
            else:
                device = Device.objects.get(
                    id=device_id,
                    site__organization=request.user.organization
                )
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get readings from the last N hours
        time_threshold = timezone.now() - timedelta(hours=hours)
        readings = PowerReading.objects.filter(
            device=device,
            timestamp__gte=time_threshold
        ).order_by('timestamp')[:500]  # Limit to 500 points for performance
        
        serializer = PowerReadingSerializer(readings, many=True)
        return Response(serializer.data)


class RelayStateView(APIView):
    """
    GET  /api/v1/telemetry/relay-states/?device_id=X — Get current relay states
    POST /api/v1/telemetry/relay-states/ — Manual override relay states
    
    The POST endpoint is called when a user clicks a relay toggle in the
    web dashboard. It overrides the DSL's automatic control.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        device_id = request.query_params.get('device_id')
        mac_address = request.query_params.get('mac')
        
        if not device_id and not mac_address:
            return Response({'error': 'device_id or mac parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if device_id:
                if request.user.is_super_admin:
                    device = Device.objects.get(id=device_id)
                else:
                    device = Device.objects.get(id=device_id, site__organization=request.user.organization)
            else:
                if request.user.is_super_admin:
                    device = Device.objects.get(mac_address=mac_address)
                else:
                    device = Device.objects.get(mac_address=mac_address, site__organization=request.user.organization)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create relay state (should already exist from DSL)
        relay_state, created = RelayState.objects.get_or_create(device=device)
        
        return Response({
            'device_id': device.id,
            'device_name': device.name,
            'relay_states': relay_state.as_list(),
            'last_source': relay_state.last_source,
            'last_updated': relay_state.last_updated.isoformat() if relay_state.last_updated else None,
        })
    
    def post(self, request):
        """Manual relay override."""
        if not request.user.is_site_manager and not request.user.is_super_admin:
            return Response({'error': 'Only site managers can override relays'},
                          status=status.HTTP_403_FORBIDDEN)
        
        device_id = request.data.get('device_id')
        relay_states = request.data.get('relay_states')
        
        if not device_id or not relay_states or len(relay_states) != 4:
            return Response({'error': 'device_id and relay_states (4 booleans) required'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if request.user.is_super_admin:
                device = Device.objects.get(id=device_id)
            else:
                device = Device.objects.get(id=device_id, site__organization=request.user.organization)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        
        relay_state, created = RelayState.objects.get_or_create(device=device)
        relay_state.update_from_list(relay_states, source='manual')
        
        # Log the manual override
        AlertLog.objects.create(
            device=device,
            event_type='manual_override',
            severity='info',
            description="User {} manually set relays to {}".format(
                request.user.username, relay_states
            ),
        )
        
        return Response({
            'status': 'ok',
            'relay_states': relay_state.as_list(),
            'last_source': 'manual',
        })


class AlertLogView(APIView):
    """
    GET /api/v1/telemetry/alerts/?device_id=X&limit=50
    
    Returns recent alert/event log entries.
    The Vue.js dashboard shows these in the scrolling alert feed.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        device_id = request.query_params.get('device_id')
        limit = int(request.query_params.get('limit', 50))
        
        # Base queryset filtered by tenant
        if request.user.is_super_admin:
            alerts = AlertLog.objects.all()
        else:
            alerts = AlertLog.objects.filter(device__site__organization=request.user.organization)
        
        if device_id:
            alerts = alerts.filter(device_id=device_id)
        
        alerts = alerts.order_by('-created_at')[:limit]
        serializer = AlertLogSerializer(alerts, many=True)
        return Response(serializer.data)
