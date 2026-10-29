import { defineStore } from 'pinia'
import api from '../api/client'

// Hardcoded test user — frontend only, remove when backend is ready
const TEST_USER = {
  username: 'testuser',
  password: 'password123',
  email: 'test@aethervane.local',
  name: 'Test User',
  role: 'super_admin',
  id: 1,
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    userRole: localStorage.getItem('user_role') || '',
    username: localStorage.getItem('username') || '',
    userId: localStorage.getItem('user_id') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isSuperAdmin: (state) => state.userRole === 'super_admin',
    isSiteManager: (state) => state.userRole === 'super_admin' || state.userRole === 'site_manager',
  },

  actions: {
    async login(username, password) {
      // ---- TEST BYPASS ----
      await new Promise((r) => setTimeout(r, 400))
      if (username === TEST_USER.username && password === TEST_USER.password) {
        this.token = 'test-token'
        this.refreshToken = 'test-refresh'
        this.userRole = TEST_USER.role
        this.username = TEST_USER.username
        this.userId = TEST_USER.id

        localStorage.setItem('access_token', this.token)
        localStorage.setItem('refresh_token', this.refreshToken)
        localStorage.setItem('user_role', this.userRole)
        localStorage.setItem('username', this.username)
        localStorage.setItem('user_id', this.userId)
        return
      }
      throw new Error('Invalid credentials')
      // ---- END TEST BYPASS ----

      // Real API call (uncomment when backend is ready):
      // const response = await api.post('/auth/login/', { username, password })
      // this.token = response.data.access
      // this.refreshToken = response.data.refresh
      // this.userRole = response.data.user_role
      // this.username = response.data.username
      // this.userId = response.data.user_id
      // localStorage.setItem('access_token', this.token)
      // localStorage.setItem('refresh_token', this.refreshToken)
      // localStorage.setItem('user_role', this.userRole)
      // localStorage.setItem('username', this.username)
      // localStorage.setItem('user_id', this.userId)
    },

    logout() {
      this.token = ''
      this.refreshToken = ''
      this.userRole = ''
      this.username = ''
      this.userId = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_role')
      localStorage.removeItem('username')
      localStorage.removeItem('user_id')
    },
  },
})