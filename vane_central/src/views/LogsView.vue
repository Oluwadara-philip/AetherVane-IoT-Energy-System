<template>
  <div class="min-h-screen pb-20 px-6 pt-6">
    <div class="mb-6">
      <h1 class="font-heading text-2xl font-bold text-white">Event Logs</h1>
      <p class="text-sm text-gray-400 mt-1">Shedding events, recoveries, and manual overrides</p>
    </div>

    <div class="glass-panel p-5">
      <div class="flex items-center gap-2 mb-4">
        <select v-model="filterType" class="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10
                        text-white text-sm focus:outline-none focus:border-electric/50">
          <option value="" class="bg-navy-800">All Events</option>
          <option value="shedding" class="bg-navy-800">Shedding</option>
          <option value="recovery" class="bg-navy-800">Recovery</option>
          <option value="manual_override" class="bg-navy-800">Manual Override</option>
          <option value="device_offline" class="bg-navy-800">Device Offline</option>
          <option value="device_online" class="bg-navy-800">Device Online</option>
        </select>
      </div>

      <div class="overflow-x-auto custom-scroll">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-white/10">
              <th class="pb-3 text-gray-400 font-medium">Time</th>
              <th class="pb-3 text-gray-400 font-medium">Type</th>
              <th class="pb-3 text-gray-400 font-medium">Severity</th>
              <th class="pb-3 text-gray-400 font-medium">Description</th>
              <th class="pb-3 text-gray-400 font-medium">SoC</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in filteredAlerts" :key="alert.id"
                class="border-b border-white/5 hover:bg-white/5 transition-colors">
              <td class="py-3 text-gray-400">{{ formatTime(alert.created_at) }}</td>
              <td class="py-3">
                <span class="px-2 py-0.5 rounded-full text-xs"
                      :class="typeClass(alert.event_type)">
                  {{ alert.event_type.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3">
                <span class="px-2 py-0.5 rounded-full text-xs"
                      :class="severityClass(alert.severity)">
                  {{ alert.severity }}
                </span>
              </td>
              <td class="py-3 text-white">{{ alert.description }}</td>
              <td class="py-3 text-gray-400">
                {{ alert.battery_pct_at_event ? alert.battery_pct_at_event.toFixed(1) + '%' : '-' }}
              </td>
            </tr>
            <tr v-if="filteredAlerts.length === 0">
              <td colspan="5" class="py-8 text-center text-gray-500">No events found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTelemetryStore } from '../stores/telemetry'

const telemetry = useTelemetryStore()
const filterType = ref('')

const filteredAlerts = computed(() => {
  if (!filterType.value) return telemetry.alerts
  return telemetry.alerts.filter(a => a.event_type === filterType.value)
})

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString()
}

function typeClass(type) {
  const classes = {
    shedding: 'bg-relay-warn/20 text-relay-warn',
    recovery: 'bg-relay-on/20 text-relay-on',
    manual_override: 'bg-electric/20 text-electric',
    device_offline: 'bg-relay-cut/20 text-relay-cut',
    device_online: 'bg-relay-on/20 text-relay-on',
    threshold_breach: 'bg-relay-warn/20 text-relay-warn',
  }
  return classes[type] || 'bg-gray-500/20 text-gray-400'
}

function severityClass(severity) {
  const classes = {
    critical: 'bg-relay-cut/20 text-relay-cut',
    warning: 'bg-relay-warn/20 text-relay-warn',
    info: 'bg-electric/20 text-electric',
  }
  return classes[severity] || 'bg-gray-500/20 text-gray-400'
}

onMounted(async () => {
  await telemetry.fetchAlerts()
})
</script>
