<template>
  <div v-if="!isLoginRoute" class="min-h-screen flex flex-col">
    <!-- Top Navigation Bar -->
    <nav class="fixed top-0 left-0 right-0 h-16 glass-panel rounded-none border-x-0 border-t-0 z-50 flex items-center justify-between px-6">
      <!-- Logo and Site Selector -->
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2">
          <Zap class="w-6 h-6 text-electric" />
          <span class="font-heading font-bold text-lg text-white">AetherVane</span>
        </div>
        <SiteSelector v-if="auth.isAuthenticated" />
      </div>

      <!-- User Menu -->
      <div class="flex items-center gap-4">
        <span v-if="auth.isAuthenticated" class="text-sm text-gray-400">
          {{ auth.username }}
          <span class="ml-2 px-2 py-0.5 rounded-full text-xs font-semibold"
                :class="roleBadgeClass">
            {{ auth.userRole.replace('_', ' ') }}
          </span>
        </span>
        <button v-if="auth.isAuthenticated" @click="handleLogout"
                class="text-gray-400 hover:text-white transition-colors flex items-center gap-1">
          <LogOut class="w-4 h-4" />
          <span class="text-sm">Logout</span>
        </button>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 pt-16">
      <router-view />
    </main>

    <!-- Bottom Navigation -->
    <nav v-if="auth.isAuthenticated" class="fixed bottom-0 left-0 right-0 h-14 glass-panel rounded-none border-x-0 border-b-0 z-50 flex items-center justify-around">
      <router-link v-for="item in navItems" :key="item.name" :to="item.path"
                   class="flex flex-col items-center gap-1 px-4 py-1 transition-colors"
                   :class="$route.name === item.name ? 'text-electric' : 'text-gray-400 hover:text-white'">
        <component :is="item.icon" class="w-5 h-5" />
        <span class="text-xs">{{ item.label }}</span>
      </router-link>
    </nav>
  </div>

  <!-- Login page has no nav -->
  <router-view v-else />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Zap, LogOut, LayoutGrid, BarChart3, Building2, ScrollText } from 'lucide-vue-next'
import { useAuthStore } from './stores/auth'
import { useTelemetryStore } from './stores/telemetry'
import SiteSelector from './components/SiteSelector.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const telemetry = useTelemetryStore()

const isLoginRoute = computed(() => route.name === 'login')

const navItems = [
  { name: 'dashboard', path: '/', label: 'Dashboard', icon: LayoutGrid },
  { name: 'analytics', path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { name: 'sites', path: '/sites', label: 'Sites', icon: Building2 },
  { name: 'logs', path: '/logs', label: 'Logs', icon: ScrollText },
]

const roleBadgeClass = computed(() => {
  switch (auth.userRole) {
    case 'super_admin': return 'bg-electric/20 text-electric border border-electric/30'
    case 'site_manager': return 'bg-relay-on/20 text-relay-on border border-relay-on/30'
    case 'viewer': return 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
    default: return 'bg-gray-500/20 text-gray-300'
  }
})

onMounted(async () => {
  if (auth.isAuthenticated) {
    await telemetry.fetchSites()
  }
})

function handleLogout() {
  telemetry.stopPolling()
  auth.logout()
  router.push('/login')
}
</script>
