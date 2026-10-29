<template>
  <div class="min-h-screen pb-20">
    <!-- Page Header -->
    <div class="px-6 pt-6 pb-4">
      <h1 class="font-heading text-2xl font-bold text-white">Dashboard</h1>
      <p class="text-sm text-gray-400 mt-1">Real-time energy monitoring and relay control</p>
    </div>

    <div v-if="telemetry.devices.length === 0" class="px-6">
      <div class="glass-panel p-8 text-center">
        <Server class="w-12 h-12 text-gray-500 mx-auto mb-3" />
        <p class="text-gray-400">No devices found for this site.</p>
        <p class="text-sm text-gray-500 mt-1">Register a device in the Sites page.</p>
      </div>
    </div>

    <div v-else class="px-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Left: Telemetry Gauges -->
      <div class="lg:col-span-2 space-y-4">
        <!-- Device Status Bar -->
        <div class="glass-panel p-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2.5 h-2.5 rounded-full"
                 :class="deviceOnline ? 'bg-relay-on animate-pulse' : 'bg-relay-cut'"></div>
            <span class="text-white font-semibold">{{ selectedDeviceName }}</span>
            <span class="text-xs text-gray-400">{{ deviceOnline ? 'Online' : 'Offline' }}</span>
          </div>
          <div class="flex gap-2">
            <button v-for="d in telemetry.devices" :key="d.id"
                    @click="telemetry.selectDevice(d.id)"
                    class="px-3 py-1 rounded-lg text-xs transition-all"
                    :class="d.id === telemetry.selectedDeviceId
                           ? 'bg-electric/20 text-electric border border-electric/30'
                           : 'bg-white/5 text-gray-400 hover:text-white'">
              {{ d.name }}
            </button>
          </div>
        </div>

        <!-- Gauges Grid -->
        <div class="grid grid-cols-2 gap-4">
          <GaugeWidget title="Battery Voltage" :value="latestReading?.voltage ?? 0" unit="V"
                       :min="10" :max="13" :thresholds="{warn: 11.5, danger: 10.8}"
                       color="#00D4FF" icon="battery" />
          <GaugeWidget title="Current Draw" :value="latestReading?.current ?? 0" unit="A"
                       :min="0" :max="30" color="#0A84FF" icon="current" />
          <GaugeWidget title="Power Consumption" :value="latestReading?.wattage ?? 0" unit="W"
                       :min="0" :max="500" color="#FFB800" icon="power" />
          <GaugeWidget title="Battery SoC" :value="latestReading?.battery_pct ?? 0" unit="%"
                       :min="0" :max="100" :thresholds="{warn: 40, danger: 15}"
                       color="#00E676" icon="battery" />
        </div>

        <!-- Relay Control Panel -->
        <div class="glass-panel p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-heading text-lg font-semibold text-white">Relay Control</h2>
            <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="telemetry.relaySource === 'dsl' ? 'bg-relay-warn/20 text-relay-warn' :
                           telemetry.relaySource === 'manual' ? 'bg-electric/20 text-electric' :
                           'bg-gray-500/20 text-gray-400'">
              {{ telemetry.relaySource === 'dsl' ? 'DSL Active' :
                  telemetry.relaySource === 'manual' ? 'Manual Override' : 'System Default' }}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <RelayToggle v-for="(state, i) in telemetry.relayStates" :key="i"
                         :relay-number="i + 1"
                         :state="state"
                         :name="relayNames[i]"
                         :can-control="auth.isSiteManager"
                         @toggle="handleRelayToggle(i)" />
          </div>
        </div>
      </div>

      <!-- Right: Alert Feed -->
      <div class="space-y-4">
        <div class="glass-panel p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-heading text-lg font-semibold text-white">Alert Feed</h2>
            <Bell class="w-5 h-5 text-gray-400" />
          </div>
          <div class="space-y-2 max-h-[500px] overflow-y-auto custom-scroll">
            <div v-for="alert in telemetry.alerts" :key="alert.id"
                 class="p-3 rounded-lg border animate-slide-up"
                 :class="alertClass(alert)">
              <div class="flex items-start gap-2">
                <AlertCircle class="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-white">{{ alert.description }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ formatTime(alert.created_at) }}</p>
                </div>
              </div>
            </div>
            <p v-if="telemetry.alerts.length === 0" class="text-center text-gray-500 text-sm py-4">
              No alerts. System running normally.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Server, Bell, AlertCircle } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useTelemetryStore } from '../stores/telemetry'
import GaugeWidget from '../components/GaugeWidget.vue'
import RelayToggle from '../components/RelayToggle.vue'

const auth = useAuthStore()
const telemetry = useTelemetryStore()
const latestReading = ref(null)

const selectedDeviceName = computed(() => {
  const d = telemetry.devices.find(d => d.id === telemetry.selectedDeviceId)
  return d ? d.name : 'No Device'
})

const deviceOnline = computed(() => {
  const d = telemetry.devices.find(d => d.id === telemetry.selectedDeviceId)
  return d ? d.device_status === 'online' : false
})

const relayNames = [
  'Essential Loads',
  'Secondary Loads',
  'Heavy Loads',
  'Extra Heavy Loads',
]

function alertClass(alert) {
  switch (alert.severity) {
    case 'critical': return 'bg-relay-cut/10 border-relay-cut/30'
    case 'warning': return 'bg-relay-warn/10 border-relay-warn/30'
    default: return 'bg-electric/10 border-electric/30'
  }
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString()
}

async function handleRelayToggle(index) {
  const newState = !telemetry.relayStates[index]
  await telemetry.toggleRelay(index, newState)
}

onMounted(() => {
  if (telemetry.selectedDeviceId) {
    telemetry.startPolling()
  }
})
</script>
