<template>
  <div class="glass-panel glass-panel-hover p-4 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-lg flex items-center justify-center"
           :class="stateClass">
        <span class="text-sm font-bold">{{ relayNumber }}</span>
      </div>
      <div>
        <p class="text-white font-medium text-sm">Relay {{ relayNumber }}</p>
        <p class="text-xs text-gray-400">{{ name }}</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <span class="text-xs font-medium" :class="stateTextColor">
        {{ state ? 'ON' : 'OFF' }}
      </span>
      <div v-if="canControl"
           class="toggle-switch"
           :class="state ? 'on' : 'off'"
           @click="$emit('toggle')">
        <div class="toggle-knob"></div>
      </div>
      <div v-else class="w-12 h-6 rounded-full flex items-center justify-center"
           :class="state ? 'bg-relay-on/20' : 'bg-gray-600/20'">
        <div class="w-3 h-3 rounded-full" :class="state ? 'bg-relay-on' : 'bg-gray-500'"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  relayNumber: { type: Number, required: true },
  state: { type: Boolean, required: true },
  name: { type: String, default: '' },
  canControl: { type: Boolean, default: false },
})

defineEmits(['toggle'])

const stateClass = computed(() => {
  return props.state
    ? 'bg-relay-on/20 border border-relay-on/30'
    : 'bg-relay-cut/20 border border-relay-cut/30'
})

const stateTextColor = computed(() => {
  return props.state ? 'text-relay-on' : 'text-relay-cut'
})
</script>
