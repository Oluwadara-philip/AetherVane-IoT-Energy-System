<template>
  <select v-if="telemetry.sites.length > 0"
          @change="handleSelect"
          class="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white text-sm
                 focus:outline-none focus:border-electric/50 cursor-pointer">
    <option v-for="site in telemetry.sites" :key="site.id" :value="site.id"
            class="bg-navy-800 text-white">
      {{ site.name }} ({{ site.device_count || 0 }} devices)
    </option>
  </select>
</template>

<script setup>
import { useTelemetryStore } from '../stores/telemetry'

const telemetry = useTelemetryStore()

function handleSelect(event) {
  telemetry.selectSite(Number(event.target.value))
}
</script>
