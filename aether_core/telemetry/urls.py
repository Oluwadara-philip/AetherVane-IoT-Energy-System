# AetherVane Telemetry App — URL Routes
# =======================================
# Routes for telemetry ingestion, history, relay states, and alerts.
# Included under /api/v1/telemetry/ (see aether_core/urls.py)

from django.urls import path
from .views import (
    TelemetryIngestView, TelemetryHistoryView,
    RelayStateView, AlertLogView
)

urlpatterns = [
    # POST /api/v1/telemetry/ingest/ — ESP32 posts sensor data here
    path('ingest/', TelemetryIngestView.as_view(), name='telemetry-ingest'),
    
    # GET /api/v1/telemetry/history/?device_id=X&hours=24 — Historical readings for charts
    path('history/', TelemetryHistoryView.as_view(), name='telemetry-history'),
    
    # GET /api/v1/telemetry/relay-states/?device_id=X — Current relay states
    # POST /api/v1/telemetry/relay-states/ — Manual relay override
    path('relay-states/', RelayStateView.as_view(), name='relay-states'),
    
    # GET /api/v1/telemetry/alerts/?device_id=X&limit=50 — Alert/event log
    path('alerts/', AlertLogView.as_view(), name='alert-logs'),
]
