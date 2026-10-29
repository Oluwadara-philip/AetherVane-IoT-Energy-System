<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <!-- Animated background particles -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div v-for="i in 20" :key="i" class="absolute rounded-full bg-electric/10"
           :style="particleStyle(i)" />
    </div>

    <!-- Login Card -->
    <div class="glass-panel p-8 w-full max-w-md animate-fade-in relative z-10">
      <div class="flex flex-col items-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-electric to-electric-dim flex items-center justify-center mb-4 animate-pulse-glow">
          <Zap class="w-8 h-8 text-white" />
        </div>
        <h1 class="font-heading text-2xl font-bold text-white">AetherVane</h1>
        <p class="text-sm text-gray-400 mt-1">Energy Monitoring & Load Shedding</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-300 mb-1.5">Username</label>
          <input v-model="username" type="text" required
                 class="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white
                        focus:outline-none focus:border-electric/50 focus:bg-white/10 transition-all"
                 placeholder="Enter your username" />
        </div>
        <div>
          <label class="block text-sm text-gray-300 mb-1.5">Password</label>
          <input v-model="password" type="password" required
                 class="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white
                        focus:outline-none focus:border-electric/50 focus:bg-white/10 transition-all"
                 placeholder="Enter your password" />
        </div>

        <p v-if="error" class="text-relay-cut text-sm text-center">{{ error }}</p>

        <button type="submit" :disabled="loading"
                class="w-full py-2.5 rounded-lg bg-gradient-to-r from-electric to-electric-dim
                       text-white font-semibold hover:opacity-90 transition-opacity
                       disabled:opacity-50 disabled:cursor-not-allowed">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Zap } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

function particleStyle(i) {
  const size = Math.random() * 6 + 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animation: `pulse-glow ${2 + Math.random() * 3}s ease-in-out infinite`,
    animationDelay: `${Math.random() * 3}s`,
  }
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = 'Invalid username or password'
  } finally {
    loading.value = false
  }
}
</script>
