<template>
  <div class="glass-panel glass-panel-hover p-5">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm text-gray-300 font-medium">{{ title }}</span>
      <component :is="iconComponent" class="w-4 h-4 text-gray-400" />
    </div>

    <!-- Circular Gauge -->
    <div class="relative flex items-center justify-center my-4">
      <svg class="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="50" fill="none"
                stroke="rgba(255,255,255,0.06)" stroke-width="8" />
        <circle cx="60" cy="60" r="50" fill="none"
                :stroke="currentStrokeColor" stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="arcDashArray"
                :stroke-dashoffset="arcDashOffset"
                style="transition: stroke-dashoffset 0.8s ease, stroke 0.3s ease" />
      </svg>
      <div class="absolute flex flex-col items-center">
        <span class="text-2xl font-bold font-heading text-white text-glow">
          {{ formattedValue }}
        </span>
        <span class="text-xs text-gray-400 mt-0.5">{{ unit }}</span>
      </div>
    </div>

    <div v-if="statusLabel" class="text-center">
      <span class="text-xs px-2 py-0.5 rounded-full" :class="statusClass">
        {{ statusLabel }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Battery, Zap, Activity } from 'lucide-vue-next'

const props = defineProps({
  title: { type: String, required: true },
  value: { type: Number, required: true },
  unit: { type: String, required: true },
  min: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  color: { type: String, default: '#00D4FF' },
  thresholds: { type: Object, default: null },
  icon: { type: String, default: 'battery' },
})

const iconMap = { battery: Battery, current: Zap, power: Activity }
const iconComponent = computed(() => iconMap[props.icon] || Battery)

const percentage = computed(() => {
  const range = props.max - props.min
  const pct = ((props.value - props.min) / range) * 100
  return Math.max(0, Math.min(100, pct))
})

const arcCircumference = 2 * Math.PI * 50
const arcDashArray = computed(() => `${arcCircumference}`)
const arcDashOffset = computed(() => {
  return arcCircumference - (percentage.value / 100) * arcCircumference * 0.75
})

const formattedValue = computed(() => {
  return props.value >= 100 ? Math.round(props.value) : props.value.toFixed(1)
})

const currentStrokeColor = computed(() => {
  if (!props.thresholds) return props.color
  if (props.thresholds.danger && props.value <= props.thresholds.danger) return '#FF3D71'
  if (props.thresholds.warn && props.value <= props.thresholds.warn) return '#FFB800'
  return props.color
})

const statusLabel = computed(() => {
  if (!props.thresholds) return ''
  if (props.thresholds.danger && props.value <= props.thresholds.danger) return 'Critical'
  if (props.thresholds.warn && props.value <= props.thresholds.warn) return 'Warning'
  return 'Normal'
})

const statusClass = computed(() => {
  if (!props.thresholds) return ''
  if (props.thresholds.danger && props.value <= props.thresholds.danger)
    return 'bg-relay-cut/20 text-relay-cut'
  if (props.thresholds.warn && props.value <= props.thresholds.warn)
    return 'bg-relay-warn/20 text-relay-warn'
  return 'bg-relay-on/20 text-relay-on'
})
</script>
