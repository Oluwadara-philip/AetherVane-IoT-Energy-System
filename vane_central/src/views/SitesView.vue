<template>
  <div class="min-h-screen pb-20 px-6 pt-6">
    <div class="mb-6">
      <h1 class="font-heading text-2xl font-bold text-white">Sites & Devices</h1>
      <p class="text-sm text-gray-400 mt-1">Manage monitored locations and registered Vane Nodes</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="site in telemetry.sites" :key="site.id"
           class="glass-panel glass-panel-hover p-5">
        <div class="flex items-center gap-3 mb-4">
          <Building2 class="w-6 h-6 text-electric" />
          <div>
            <h3 class="font-heading text-lg font-semibold text-white">{{ site.name }}</h3>
            <p class="text-xs text-gray-400">{{ site.location || 'No location set' }}</p>
          </div>
        </div>

        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-400">Devices</span>
          <span class="text-white font-semibold">{{ site.device_count || 0 }}</span>
        </div>

        <div v-if="devicesForSite(site.id).length > 0" class="mt-4 space-y-2">
          <div v-for="device in devicesForSite(site.id)" :key="device.id"
               class="flex items-center justify-between p-3 rounded-lg bg-white/5">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full"
                   :class="device.device_status === 'online' ? 'bg-relay-on' : 'bg-relay-cut'"></div>
              <div>
                <p class="text-white text-sm font-medium">{{ device.name }}</p>
                <p class="text-xs text-gray-500">{{ device.mac_address }}</p>
              </div>
            </div>
            <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="device.device_status === 'online'
                         ? 'bg-relay-on/20 text-relay-on'
                         : 'bg-relay-cut/20 text-relay-cut'">
              {{ device.device_status }}
            </span>
          </div>
        </div>

        <button @click="telemetry.selectSite(site.id)"
                class="w-full mt-4 py-2 rounded-lg bg-electric/10 text-electric border border-electric/20
                       hover:bg-electric/20 transition-colors text-sm">
          View Dashboard
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Building2 } from 'lucide-vue-next'
import { useTelemetryStore } from '../stores/telemetry'

const telemetry = useTelemetryStore()

function devicesForSite(siteId) {
  return telemetry.devices.filter(d => d.site === siteId)
}

onMounted(async () => {
  await telemetry.fetchSites()
})
</script>
