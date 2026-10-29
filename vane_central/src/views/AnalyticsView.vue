<template>
  <div class="min-h-screen pb-20 px-6 pt-6">
    <div class="mb-6">
      <h1 class="font-heading text-2xl font-bold text-white">Analytics</h1>
      <p class="text-sm text-gray-400 mt-1">Historical energy consumption and voltage trends</p>
    </div>

    <div v-if="telemetry.historyData.length === 0" class="glass-panel p-8 text-center">
      <BarChart3 class="w-12 h-12 text-gray-500 mx-auto mb-3" />
      <p class="text-gray-400">No history data available.</p>
      <button @click="loadHistory" class="mt-3 px-4 py-2 rounded-lg bg-electric/20 text-electric
                                   border border-electric/30 hover:bg-electric/30 transition-colors">
        Load 24h History
      </button>
    </div>

    <div v-else class="space-y-4">
      <div class="glass-panel p-5">
        <h2 class="font-heading text-lg font-semibold text-white mb-4">Voltage Trend (24h)</h2>
        <EnergyChart :data="voltageData" color="#00D4FF" y-label="Voltage (V)" />
      </div>

      <div class="glass-panel p-5">
        <h2 class="font-heading text-lg font-semibold text-white mb-4">Power Consumption (24h)</h2>
        <EnergyChart :data="wattageData" color="#FFB800" y-label="Power (W)" />
      </div>

      <div class="glass-panel p-5">
        <h2 class="font-heading text-lg font-semibold text-white mb-4">Battery SoC (24h)</h2>
        <EnergyChart :data="batteryData" color="#00E676" y-label="SoC (%)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { BarChart3 } from 'lucide-vue-next'
import { useTelemetryStore } from '../stores/telemetry'
import EnergyChart from '../components/EnergyChart.vue'

const telemetry = useTelemetryStore()

const voltageData = computed(() =>
  telemetry.historyData.map(r => [new Date(r.timestamp).getTime(), r.voltage])
)

const wattageData = computed(() =>
  telemetry.historyData.map(r => [new Date(r.timestamp).getTime(), r.wattage])
)

const batteryData = computed(() =>
  telemetry.historyData.map(r => [new Date(r.timestamp).getTime(), r.battery_pct])
)

async function loadHistory() {
  await telemetry.fetchHistory(24)
}

onMounted(() => {
  if (telemetry.selectedDeviceId) {
    loadHistory()
  }
})
</script>
